/*
 * physics.cpp - محرك فيزياء C++ متكامل
 * 
 * التجميع لأندرويد:
 * $ANDROID_NDK/bin/aarch64-linux-android-clang++ -O3 -shared -std=c++17 -fPIC \
 *   `python3 -m pybind11 --includes` physics.cpp -o physics_cpp.so
 * 
 * التجميع للينكس:
 * g++ -O3 -shared -std=c++17 -fPIC `python3 -m pybind11 --includes` physics.cpp -o physics_cpp.so
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <queue>
#include <mutex>

namespace py = pybind11;

// ==================== الثوابت ====================
constexpr double PI = 3.14159265358979323846;
constexpr double DEG_TO_RAD = PI / 180.0;

// ==================== 1. فئة الرصاصة المحسنة ====================
class OptimizedBullet {
public:
    double x, y, angle, speed;
    bool active;
    double distance_traveled;
    double max_distance;
    bool hit;
    int id;
    
    OptimizedBullet(int id, double x, double y, double angle, double speed, double max_dist)
        : id(id), x(x), y(y), angle(angle), speed(speed), max_distance(max_dist),
          active(true), distance_traveled(0), hit(false) {}
    
    void update(double dt) {
        if (!active || hit) return;
        double rad = angle * DEG_TO_RAD;
        double move_x = speed * std::cos(rad);
        double move_y = speed * std::sin(rad);
        x += move_x * dt;
        y += move_y * dt;
        distance_traveled += speed * dt;
    }
    
    bool should_remove(double screen_width, double screen_height) {
        return (!active) || hit ||
               x < -100 || x > screen_width + 100 ||
               y < -100 || y > screen_height + 100 ||
               distance_traveled > max_distance;
    }
    
    bool check_collision(double other_x, double other_y, double other_w, double other_h) {
        return (x < other_x + other_w && x + 10 > other_x &&
                y < other_y + other_h && y + 10 > other_y);
    }
};

// ==================== 2. تجمع الرصاص المحسن (Bullet Pool) ====================
class BulletPool {
private:
    std::vector<OptimizedBullet> pool;
    int pool_size;
    int next_index;
    std::mutex pool_mutex;
    
public:
    BulletPool(int size) : pool_size(size), next_index(0) {
        pool.reserve(size);
        for (int i = 0; i < size; ++i) {
            pool.emplace_back(i, 0, 0, 0, 0, 0);
            pool.back().active = false;
        }
    }
    
    int get_bullet(double x, double y, double angle, double speed, double max_dist) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        
        // البحث عن رصاصة غير نشطة
        for (int i = 0; i < pool_size; ++i) {
            if (!pool[i].active) {
                pool[i].x = x;
                pool[i].y = y;
                pool[i].angle = angle;
                pool[i].speed = speed;
                pool[i].max_distance = max_dist;
                pool[i].distance_traveled = 0;
                pool[i].hit = false;
                pool[i].active = true;
                return pool[i].id;
            }
        }
        
        // إعادة استخدام أقدم رصاصة
        int id = next_index;
        pool[next_index].x = x;
        pool[next_index].y = y;
        pool[next_index].angle = angle;
        pool[next_index].speed = speed;
        pool[next_index].max_distance = max_dist;
        pool[next_index].distance_traveled = 0;
        pool[next_index].hit = false;
        pool[next_index].active = true;
        next_index = (next_index + 1) % pool_size;
        return id;
    }
    
    void return_bullet(int id) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        if (id >= 0 && id < pool_size) {
            pool[id].active = false;
        }
    }
    
    void update_bullets(double dt, double screen_width, double screen_height) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        for (auto& bullet : pool) {
            if (bullet.active && !bullet.hit) {
                bullet.update(dt);
            }
        }
    }
    
    std::vector<int> get_active_bullets() {
        std::lock_guard<std::mutex> lock(pool_mutex);
        std::vector<int> active_ids;
        for (const auto& bullet : pool) {
            if (bullet.active && !bullet.hit) {
                active_ids.push_back(bullet.id);
            }
        }
        return active_ids;
    }
    
    OptimizedBullet& get_bullet_by_id(int id) {
        return pool[id];
    }
    
    int size() const { return pool_size; }
};

// ==================== 3. الشبكة المكانية (Spatial Grid) ====================
class SpatialGrid {
private:
    int cell_size;
    int cols, rows;
    std::vector<std::vector<std::vector<int>>> grid;  // [col][row] -> list of entity ids
    std::unordered_map<int, std::pair<double, double>> positions;
    int next_id;
    std::mutex grid_mutex;
    
    int get_col(double x) { return std::max(0, std::min(cols - 1, static_cast<int>(x / cell_size))); }
    int get_row(double y) { return std::max(0, std::min(rows - 1, static_cast<int>(y / cell_size))); }
    
public:
    SpatialGrid(int width, int height, int cell_size = 150)
        : cell_size(cell_size), next_id(0) {
        cols = width / cell_size + 2;
        rows = height / cell_size + 2;
        grid.resize(cols, std::vector<std::vector<int>>(rows));
    }
    
    int add_entity(double x, double y) {
        std::lock_guard<std::mutex> lock(grid_mutex);
        int id = next_id++;
        positions[id] = {x, y};
        int col = get_col(x);
        int row = get_row(y);
        grid[col][row].push_back(id);
        return id;
    }
    
    void update_position(int id, double x, double y) {
        std::lock_guard<std::mutex> lock(grid_mutex);
        if (positions.find(id) == positions.end()) return;
        
        auto [old_x, old_y] = positions[id];
        int old_col = get_col(old_x);
        int old_row = get_col(old_y);
        int new_col = get_col(x);
        int new_row = get_row(y);
        
        if (old_col != new_col || old_row != new_row) {
            // إزالة من الخلية القديمة
            auto& old_cell = grid[old_col][old_row];
            old_cell.erase(std::remove(old_cell.begin(), old_cell.end(), id), old_cell.end());
            
            // إضافة إلى الخلية الجديدة
            grid[new_col][new_row].push_back(id);
        }
        
        positions[id] = {x, y};
    }
    
    void remove_entity(int id) {
        std::lock_guard<std::mutex> lock(grid_mutex);
        if (positions.find(id) == positions.end()) return;
        
        auto [x, y] = positions[id];
        int col = get_col(x);
        int row = get_row(y);
        auto& cell = grid[col][row];
        cell.erase(std::remove(cell.begin(), cell.end(), id), cell.end());
        positions.erase(id);
    }
    
    std::vector<int> get_nearby(double x, double y, double radius) {
        std::lock_guard<std::mutex> lock(grid_mutex);
        std::vector<int> result;
        int start_col = std::max(0, static_cast<int>((x - radius) / cell_size));
        int end_col = std::min(cols - 1, static_cast<int>((x + radius) / cell_size) + 1);
        int start_row = std::max(0, static_cast<int>((y - radius) / cell_size));
        int end_row = std::min(rows - 1, static_cast<int>((y + radius) / cell_size) + 1);
        
        for (int col = start_col; col <= end_col; ++col) {
            for (int row = start_row; row <= end_row; ++row) {
                for (int id : grid[col][row]) {
                    result.push_back(id);
                }
            }
        }
        return result;
    }
    
    void clear() {
        std::lock_guard<std::mutex> lock(grid_mutex);
        for (auto& col : grid)
            for (auto& cell : col)
                cell.clear();
        positions.clear();
        next_id = 0;
    }
};

// ==================== 4. مصفوفة الحركة (Movement Array) ====================
class MovementArray {
private:
    std::vector<double> x, y, vx, vy;
    std::vector<bool> active;
    int size;
    
public:
    MovementArray(int max_size) : size(max_size) {
        x.resize(max_size);
        y.resize(max_size);
        vx.resize(max_size);
        vy.resize(max_size);
        active.resize(max_size, false);
    }
    
    int add_entity(double start_x, double start_y, double start_vx, double start_vy) {
        for (int i = 0; i < size; ++i) {
            if (!active[i]) {
                x[i] = start_x;
                y[i] = start_y;
                vx[i] = start_vx;
                vy[i] = start_vy;
                active[i] = true;
                return i;
            }
        }
        return -1;
    }
    
    void update_all(double dt, double screen_width, double screen_height) {
        for (int i = 0; i < size; ++i) {
            if (active[i]) {
                x[i] += vx[i] * dt;
                y[i] += vy[i] * dt;
                
                // حدود الشاشة
                if (x[i] < 0) x[i] = 0;
                if (x[i] > screen_width) x[i] = screen_width;
                if (y[i] < 0) y[i] = 0;
                if (y[i] > screen_height) y[i] = screen_height;
            }
        }
    }
    
    void remove_entity(int index) {
        if (index >= 0 && index < size) {
            active[index] = false;
        }
    }
    
    std::vector<std::tuple<double, double, double, double, bool>> get_all() {
        std::vector<std::tuple<double, double, double, double, bool>> result;
        for (int i = 0; i < size; ++i) {
            result.emplace_back(x[i], y[i], vx[i], vy[i], active[i]);
        }
        return result;
    }
    
    void set_velocity(int index, double new_vx, double new_vy) {
        if (index >= 0 && index < size && active[index]) {
            vx[index] = new_vx;
            vy[index] = new_vy;
        }
    }
};

// ==================== 5. نظام التصادم الشامل ====================
class CollisionSystem {
private:
    SpatialGrid spatial_grid;
    BulletPool* bullet_pool;
    std::vector<std::tuple<int, double, double, double, double>> enemies; // id, x, y, w, h
    std::mutex collision_mutex;
    
public:
    CollisionSystem(int width, int height, int cell_size = 150)
        : spatial_grid(width, height, cell_size), bullet_pool(nullptr) {}
    
    void set_bullet_pool(BulletPool* pool) {
        bullet_pool = pool;
    }
    
    void add_enemy(int id, double x, double y, double w, double h) {
        std::lock_guard<std::mutex> lock(collision_mutex);
        enemies.emplace_back(id, x, y, w, h);
        spatial_grid.add_entity(x, y);
    }
    
    void update_enemy_position(int id, double x, double y) {
        spatial_grid.update_position(id, x, y);
        for (auto& enemy : enemies) {
            if (std::get<0>(enemy) == id) {
                std::get<1>(enemy) = x;
                std::get<2>(enemy) = y;
                break;
            }
        }
    }
    
    void remove_enemy(int id) {
        std::lock_guard<std::mutex> lock(collision_mutex);
        spatial_grid.remove_entity(id);
        enemies.erase(std::remove_if(enemies.begin(), enemies.end(),
            [id](const auto& e) { return std::get<0>(e) == id; }), enemies.end());
    }
    
    std::vector<int> check_bullet_collisions(double player_x, double player_y, double player_w, double player_h) {
        std::vector<int> hit_enemies;
        
        if (!bullet_pool) return hit_enemies;
        
        std::lock_guard<std::mutex> lock(collision_mutex);
        
        for (const auto& enemy : enemies) {
            int enemy_id = std::get<0>(enemy);
            double ex = std::get<1>(enemy);
            double ey = std::get<2>(enemy);
            double ew = std::get<3>(enemy);
            double eh = std::get<4>(enemy);
            
            // البحث عن الرصاصات القريبة
            auto nearby = spatial_grid.get_nearby(ex, ey, 100);
            
            for (int bullet_id : nearby) {
                if (bullet_pool) {
                    auto& bullet = bullet_pool->get_bullet_by_id(bullet_id);
                    if (bullet.active && !bullet.hit) {
                        if (bullet.check_collision(ex, ey, ew, eh)) {
                            bullet.hit = true;
                            hit_enemies.push_back(enemy_id);
                            break;
                        }
                    }
                }
            }
        }
        
        return hit_enemies;
    }
    
    bool check_player_collision(double player_x, double player_y, double player_w, double player_h) {
        std::lock_guard<std::mutex> lock(collision_mutex);
        
        for (const auto& enemy : enemies) {
            double ex = std::get<1>(enemy);
            double ey = std::get<2>(enemy);
            double ew = std::get<3>(enemy);
            double eh = std::get<4>(enemy);
            
            if (player_x < ex + ew && player_x + player_w > ex &&
                player_y < ey + eh && player_y + player_h > ey) {
                return true;
            }
        }
        return false;
    }
    
    void clear() {
        std::lock_guard<std::mutex> lock(collision_mutex);
        enemies.clear();
        spatial_grid.clear();
    }
};

// ==================== 6. دوال مساعدة محسنة ====================
double fast_distance(double x1, double y1, double x2, double y2) {
    double dx = x2 - x1;
    double dy = y2 - y1;
    return std::sqrt(dx*dx + dy*dy);
}

double fast_distance_squared(double x1, double y1, double x2, double y2) {
    double dx = x2 - x1;
    double dy = y2 - y1;
    return dx*dx + dy*dy;
}

void move_towards(double& x, double& y, double target_x, double target_y, double speed, double dt) {
    double dx = target_x - x;
    double dy = target_y - y;
    double dist = std::sqrt(dx*dx + dy*dy);
    if (dist > 0.01) {
        double move = speed * dt;
        if (move > dist) move = dist;
        x += (dx / dist) * move;
        y += (dy / dist) * move;
    }
}

// ==================== تعريف الموديول ====================
PYBIND11_MODULE(physics_cpp, m) {
    m.doc() = "C++ physics engine for Galaxy Shooter - High Performance";
    
    // فئة الرصاصة
    py::class_<OptimizedBullet>(m, "OptimizedBullet")
        .def(py::init<int, double, double, double, double, double>())
        .def_readwrite("x", &OptimizedBullet::x)
        .def_readwrite("y", &OptimizedBullet::y)
        .def_readwrite("angle", &OptimizedBullet::angle)
        .def_readwrite("speed", &OptimizedBullet::speed)
        .def_readwrite("active", &OptimizedBullet::active)
        .def_readwrite("hit", &OptimizedBullet::hit)
        .def_readwrite("distance_traveled", &OptimizedBullet::distance_traveled)
        .def_readwrite("id", &OptimizedBullet::id)
        .def("update", &OptimizedBullet::update)
        .def("should_remove", &OptimizedBullet::should_remove)
        .def("check_collision", &OptimizedBullet::check_collision);
    
    // تجمع الرصاص
    py::class_<BulletPool>(m, "BulletPool")
        .def(py::init<int>())
        .def("get_bullet", &BulletPool::get_bullet)
        .def("return_bullet", &BulletPool::return_bullet)
        .def("update_bullets", &BulletPool::update_bullets)
        .def("get_active_bullets", &BulletPool::get_active_bullets)
        .def("size", &BulletPool::size);
    
    // الشبكة المكانية
    py::class_<SpatialGrid>(m, "SpatialGrid")
        .def(py::init<int, int, int>())
        .def("add_entity", &SpatialGrid::add_entity)
        .def("update_position", &SpatialGrid::update_position)
        .def("remove_entity", &SpatialGrid::remove_entity)
        .def("get_nearby", &SpatialGrid::get_nearby)
        .def("clear", &SpatialGrid::clear);
    
    // مصفوفة الحركة
    py::class_<MovementArray>(m, "MovementArray")
        .def(py::init<int>())
        .def("add_entity", &MovementArray::add_entity)
        .def("update_all", &MovementArray::update_all)
        .def("remove_entity", &MovementArray::remove_entity)
        .def("get_all", &MovementArray::get_all)
        .def("set_velocity", &MovementArray::set_velocity);
    
    // نظام التصادم
    py::class_<CollisionSystem>(m, "CollisionSystem")
        .def(py::init<int, int, int>())
        .def("set_bullet_pool", &CollisionSystem::set_bullet_pool)
        .def("add_enemy", &CollisionSystem::add_enemy)
        .def("update_enemy_position", &CollisionSystem::update_enemy_position)
        .def("remove_enemy", &CollisionSystem::remove_enemy)
        .def("check_bullet_collisions", &CollisionSystem::check_bullet_collisions)
        .def("check_player_collision", &CollisionSystem::check_player_collision)
        .def("clear", &CollisionSystem::clear);
    
    // دوال مساعدة
    m.def("fast_distance", &fast_distance);
    m.def("fast_distance_squared", &fast_distance_squared);
    m.def("move_towards", &move_towards);
}