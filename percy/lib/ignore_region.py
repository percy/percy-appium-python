class IgnoreRegion:
    def __init__(self, top, bottom, left, right):
        if top < 0 or bottom < 0 or left < 0 or right < 0:
            raise ValueError('Only Positive integer is allowed!')

        if top >= bottom or left >= right:
            raise ValueError('Invalid ignore region parameters!')

        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def is_valid(self, height, width):
        if self.top >= height or self.bottom > height or self.left >= width or self.right > width:
            return False

        return True
