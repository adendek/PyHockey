from data.controls.AbstractGameControls import AbstractGameControls


class CameraGameControls(AbstractGameControls):

    def get_players_positions(self):
        return self.p1, self.p2
