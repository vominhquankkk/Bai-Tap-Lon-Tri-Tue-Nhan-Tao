import pygame # type: ignore
import sys
import heapq
import random  

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ring Sorting Game")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)
BROWN = (165, 42, 42)

# Ánh xạ màu cho các vòng
COLOR_MAP = {
    'red': RED,
    'pink': PINK,
    'purple': PURPLE,
    'brown': BROWN
}

# Trạng thái ban đầu
# INITIAL_STATE = [
#     ['brown', 'purple', 'pink', 'red'],  # Cột A
#     ['red', 'brown', 'purple', 'pink'],  # Cột B
#     ['pink', 'red', 'brown', 'purple'],  # Cột C
#     ['purple', 'pink', 'red', 'brown'],  # Cột D
#     [],                                  # Cột E
#     []                                   # Cột F
# ]

COLORS = ['red', 'pink', 'purple', 'brown']

# Nhãn cột
POLES = ['A', 'B', 'C', 'D', 'E', 'F']

# Kích thước cột và vòng
POLE_WIDTH = 100
POLE_HEIGHT = 400
RING_HEIGHT = 80
RING_WIDTH = 80
SPACING = 120

# Vị trí các cột
POLE_POSITIONS = [(i * SPACING + 50, 100) for i in range(6)]

# Số bước tối đa
MOVE_LIMIT = 50

def generate_random_state():
    """Tạo trạng thái ngẫu nhiên nhưng đảm bảo có thể giải được."""
    rings = COLORS * 4
    random.shuffle(rings)
    state = [rings[i * 4:(i + 1) * 4] for i in range(4)]
    state.append([])
    state.append([])
    return state


# Hàm vẽ cột
def draw_poles():
    for i, pos in enumerate(POLE_POSITIONS):
        pygame.draw.rect(screen, BLACK, (pos[0], pos[1], POLE_WIDTH, POLE_HEIGHT), 2)
        font = pygame.font.Font(None, 36)
        text = font.render(POLES[i], True, BLACK)
        screen.blit(text, (pos[0] + 30, pos[1] - 30))

# Hàm vẽ vòng
def draw_rings(state):
    for i, pole in enumerate(state):
        x = POLE_POSITIONS[i][0] + 10
        for j, color in enumerate(pole):
            y = POLE_POSITIONS[i][1] + POLE_HEIGHT - (j + 1) * RING_HEIGHT
            pygame.draw.rect(screen, COLOR_MAP[color], (x, y, RING_WIDTH, RING_HEIGHT))

# Hàm vẽ nút
def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (x + 10, y + 10))

# Hàm vẽ số bước đã thực hiện và giới hạn bước
def draw_move_count(moves, x, y):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Moves: {len(moves)}/{MOVE_LIMIT}", True, BLACK)
    screen.blit(text, (x, y))

# Hàm in các bước di chuyển ra terminal (bằng tiếng Anh)
def print_moves(moves, new_move=None):
    if new_move:
        moves.append(new_move)
    print("\nMove History:")
    if not moves:
        print("No moves yet.")
    else:
        for i, move in enumerate(moves, 1):
            from_pole, to_pole = move
            print(f"Step {i}: Pole {POLES[from_pole]} -> Pole {POLES[to_pole]}")

# Kiểm tra trạng thái mục tiêu
def is_goal(state):
    sorted_poles = 0
    empty_poles = 0
    for pole in state:
        if len(pole) == 0:
            empty_poles += 1
        elif len(pole) == 4 and len(set(pole)) == 1:
            sorted_poles += 1
    return sorted_poles == 4 and empty_poles == 2

# Hàm heuristic cho A*
def heuristic(state):
    sorted_poles = sum(1 for pole in state if len(pole) == 4 and len(set(pole)) == 1)
    return 4 - sorted_poles

# Tạo các trạng thái tiếp theo
def successors(state):
    for i in range(6):
        if state[i]:
            c = state[i][-1]
            k = 1
            while k < len(state[i]) and state[i][-k-1] == c:
                k += 1
            for j in range(6):
                if j != i:
                    if (len(state[j]) == 0 or (state[j][-1] == c and len(state[j]) + k <= 4)):
                        new_pole_i = state[i][:-k] if k < len(state[i]) else []
                        new_pole_j = state[j] + [c] * k
                        new_state = state[:]
                        new_state[i] = new_pole_i
                        new_state[j] = new_pole_j
                        new_state_tuple = tuple(map(tuple, new_state))
                        yield (new_state, new_state_tuple, (i, j))

# Thuật toán A*
def a_star(initial_state):
    initial_tuple = tuple(map(tuple, initial_state))
    visited = set()
    parent = {}
    g_scores = {initial_tuple: 0}
    queue = []
    h = heuristic(initial_state)
    heapq.heappush(queue, (h, 0, initial_state, initial_tuple))
    
    while queue:
        f, g, current_state, current_tuple = heapq.heappop(queue)
        if current_tuple in visited:
            continue
        visited.add(current_tuple)
        
        if is_goal(current_state):
            path = []
            state = current_state
            state_tuple = current_tuple
            while state_tuple in parent:
                prev_state, prev_tuple, move = parent[state_tuple]
                path.append(move)
                state = prev_state
                state_tuple = prev_tuple
            path.reverse()
            return path
        
        for new_state, new_state_tuple, move in successors(current_state):
            if new_state_tuple not in visited:
                new_g = g + 1
                if new_state_tuple not in g_scores or new_g < g_scores[new_state_tuple]:
                    g_scores[new_state_tuple] = new_g
                    h = heuristic(new_state)
                    f = new_g + h
                    heapq.heappush(queue, (f, new_g, new_state, new_state_tuple))
                    parent[new_state_tuple] = (current_state, current_tuple, move)
    return None

# Hàm chính
def main():
    initial_state = generate_random_state()  # Lưu trạng thái ban đầu
    state = [list(pole) for pole in initial_state]  # Tạo bản sao để chơi
    dragging = False
    selected_pole = None
    moves = []

    while True:
        screen.fill(WHITE)
        draw_poles()
        draw_rings(state)
        
        # Vẽ các nút
        draw_button("Reset", 50, 550, 100, 40, GRAY)
        draw_button("Solve", 200, 550, 100, 40, GRAY)
        draw_button("Quit", 350, 550, 100, 40, GRAY)
        
        # Vẽ số bước đã thực hiện và giới hạn bước
        draw_move_count(moves, 600, 20)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Kiểm tra nhấp vào nút
                if 50 <= x <= 150 and 550 <= y <= 590:  # Nếu nhấn nút Reset
                    state = [list(pole) for pole in initial_state]  # Quay về trạng thái ban đầu
                    moves = []
                    print("\nGame reset. Move history cleared.")

                    # Cập nhật lại màn hình ngay lập tức
                    screen.fill(WHITE)
                    draw_poles()
                    draw_rings(state)
                    draw_move_count(moves, 600, 20)
                    pygame.display.flip()

                elif 200 <= x <= 300 and 550 <= y <= 590:
                    solution = a_star(state)
                    if solution:
                        moves.extend(solution)  # Thêm các bước từ A* vào moves
                        for move in solution:
                            from_pole, to_pole = move
                            c = state[from_pole][-1]
                            k = 1
                            while k < len(state[from_pole]) and state[from_pole][-k-1] == c:
                                k += 1
                            state[to_pole].extend([c] * k)
                            state[from_pole] = state[from_pole][:-k]
                            print_moves(moves)  # In các bước ra terminal
                            pygame.time.wait(500)
                            screen.fill(WHITE)
                            draw_poles()
                            draw_rings(state)
                            draw_move_count(moves, 600, 20)  # Cập nhật số bước
                            pygame.display.flip()
                    else:
                        print("No solution found!")
                elif 350 <= x <= 450 and 550 <= y <= 590:
                    pygame.quit()
                    sys.exit()
                else:
                    # Kiểm tra nhấp vào cột
                    for i, pos in enumerate(POLE_POSITIONS):
                        if pos[0] <= x <= pos[0] + POLE_WIDTH and pos[1] <= y <= pos[1] + POLE_HEIGHT:
                            if state[i]:
                                selected_pole = i
                                dragging = True
                                break
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                x, y = event.pos
                for i, pos in enumerate(POLE_POSITIONS):
                    if pos[0] <= x <= pos[0] + POLE_WIDTH and pos[1] <= y <= pos[1] + POLE_HEIGHT:
                        if i != selected_pole and selected_pole is not None:
                            if state[selected_pole]:
                                c = state[selected_pole][-1]
                                k = 1
                                while k < len(state[selected_pole]) and state[selected_pole][-k-1] == c:
                                    k += 1
                                if (len(state[i]) == 0 or (state[i][-1] == c and len(state[i]) + k <= 4)):
                                    state[i].extend([c] * k)
                                    state[selected_pole] = state[selected_pole][:-k]
                                    new_move = (selected_pole, i)
                                    print_moves(moves, new_move)  # In lịch sử di chuyển ra terminal
                dragging = False
                selected_pole = None
        
        if is_goal(state):
            font = pygame.font.Font(None, 72)
            text = font.render("You Win!", True, RED)
            screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2000)  # Đợi 2 giây trước khi khởi động lại
            state = generate_random_state()  # Khởi động lại với trạng thái mới
            moves = []  # Xóa lịch sử bước di chuyển

        elif len(moves) >= MOVE_LIMIT:
            font = pygame.font.Font(None, 72)
            text = font.render("Game Over! Move Limit Reached!", True, RED)
            screen.blit(text, (WIDTH // 2 - 250, HEIGHT // 2))
        
        pygame.display.flip()

if __name__ == "__main__":
    main()