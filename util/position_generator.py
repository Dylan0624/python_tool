# util/position_generator.py
from function.ImageReconstructor import StartCorner, FirstDirection

class PositionGenerator:
    def __init__(self, params):
        self.target_width = params["target_width"]
        self.target_height = params["target_height"]
        self.start_corner = params["start_corner"]
        self.first_direction = params["first_direction"]
        self.second_direction = params["second_direction"]
        
        # 根據起始角落決定起點位置和可移動方向
        if self.start_corner == StartCorner.TOP_LEFT:
            self.current_x, self.current_y = 0, 0
            self.can_move_right = True
            self.can_move_down = True
        elif self.start_corner == StartCorner.TOP_RIGHT:
            self.current_x = self.target_width - 1
            self.current_y = 0
            self.can_move_right = False
            self.can_move_down = True
        elif self.start_corner == StartCorner.BOTTOM_LEFT:
            self.current_x = 0
            self.current_y = self.target_height - 1
            self.can_move_right = True
            self.can_move_down = False
        else:  # BOTTOM_RIGHT
            self.current_x = self.target_width - 1
            self.current_y = self.target_height - 1
            self.can_move_right = False
            self.can_move_down = False
    
    def generate_path(self):
        positions = []
        moving_horizontally = self.first_direction in [FirstDirection.LEFT, FirstDirection.RIGHT]
        
        # 初始化當前位置和移動方向
        current_x, current_y = self.current_x, self.current_y
        can_move_right = self.can_move_right
        can_move_down = self.can_move_down
        
        # 設置初始方向
        if moving_horizontally:
            if self.first_direction == FirstDirection.RIGHT:
                dx = 1 if can_move_right else -1
            else:  # LEFT
                dx = -1 if not can_move_right else 1
            dy = 0
        else:
            if self.first_direction == FirstDirection.DOWN:
                dy = 1 if can_move_down else -1
            else:  # UP
                dy = -1 if not can_move_down else 1
            dx = 0
        
        # 生成路徑
        total_positions = self.target_width * self.target_height
        while len(positions) < total_positions:
            positions.append((current_x, current_y))
            
            next_x = current_x + dx
            next_y = current_y + dy
            
            if moving_horizontally:
                if next_x < 0 or next_x >= self.target_width or (next_x, next_y) in positions:
                    if can_move_down:
                        next_y = current_y + 1
                        if next_y >= self.target_height:
                            can_move_down = False
                            next_y = current_y - 1
                    else:
                        next_y = current_y - 1
                        if next_y < 0:
                            can_move_down = True
                            next_y = current_y + 1
                    
                    if 0 <= next_y < self.target_height and (current_x, next_y) not in positions:
                        current_y = next_y
                        dx = -dx
                    else:
                        break
                else:
                    current_x = next_x
            else:
                if next_y < 0 or next_y >= self.target_height or (next_x, next_y) in positions:
                    if can_move_right:
                        next_x = current_x + 1
                        if next_x >= self.target_width:
                            can_move_right = False
                            next_x = current_x - 1
                    else:
                        next_x = current_x - 1
                        if next_x < 0:
                            can_move_right = True
                            next_x = current_x + 1
                    
                    if 0 <= next_x < self.target_width and (next_x, current_y) not in positions:
                        current_x = next_x
                        dy = -dy
                    else:
                        break
                else:
                    current_y = next_y
        
        return positions