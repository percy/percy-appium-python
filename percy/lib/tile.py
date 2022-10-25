class Tile:
    def __init__(self, filepath, status_bar_height, nav_bar_height, header_height, footer_height,
                 fullscreen=False) -> None:
        self.filepath = filepath
        self.status_bar_height = status_bar_height
        self.nav_bar_height = nav_bar_height
        self.header_height = header_height
        self.footer_height = footer_height
        self.fullscreen = fullscreen

    def __iter__(self):
        properties = [
            {'key': 'filepath', 'value': self.filepath},
            {'key': 'status_bar_height', 'value': self.status_bar_height},
            {'key': 'nav_bar_height', 'value': self.nav_bar_height},
            {'key': 'header_height', 'value': self.header_height},
            {'key': 'footer_height', 'value': self.footer_height},
            {'key': 'fullscreen', 'value': self.fullscreen}
        ]

        for prop in properties:
            yield prop['key'], prop['value']
