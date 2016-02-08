import cv2


class VideoCapture2():
    def __init__(self, res):
        """

        :param res: resolution tuple
        """
        self.res = res

        self.camWindow = 'cam'
        self.helpWindow = 'help'

        self.cap = cv2.VideoCapture(0)
        cv2.namedWindow(self.camWindow, cv2.CV_WINDOW_AUTOSIZE)
        # cv2.namedWindow(self.helpWindow, cv2.CV_WINDOW_AUTOSIZE)
        # cv2.namedWindow('help2', cv2.CV_WINDOW_AUTOSIZE)

        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        self.players = None

        # prevoius position for calculating speed
        self.oldPos = [(0, 0), (0, 0)]

    def getFrame(self):
        _, frame = self.cap.read()
        return cv2.resize(cv2.flip(frame, 1), self.res)

    def findPlayers2(self):
        while True:
            frame = self.getFrame()

            # draw two circles for players
            r = 30

            x = self.res[0] / 4
            y = self.res[1] / 2

            z1 = (x, y)
            z2 = (3 * x, y)

            cv2.circle(frame, z1, r, [255, 0, 0], 5)
            cv2.circle(frame, z2, r, [0, 255, 0], 5)

            key = cv2.waitKey(10) & 0xFF
            if key == ord('o'):
                return [(z1 + (r,)), (z2 + (r,))], self.getFrame()

            cv2.imshow(self.camWindow, frame)

    @staticmethod
    def parsePlayers(circles, frame):
        # result to return
        players = []

        windows = ['help', 'help2']

        i = 0
        for c in circles:
            # parse each incoming circle to square

            square = (int(c[0] - c[2]), int(c[1] - c[2]), int(2 * c[2]), int(2 * c[2]))
            roi = frame[square[1]:(square[1] + square[2]), square[0]:(square[0] + square[2]), :]

            # cv2.rectangle(frame, (square[0], square[1]), (square[0] + square[2], square[1] + square[2]), 255, 3)

            # cv2.imshow('help2', frame)
            # cv2.imshow(windows[i], roi)

            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            color = [0, 0, 0]
            color[i] = 255
            i += 1

            # create info about both players
            players.append([
                square,  # first position
                cv2.calcHist([hsv_roi], [0], None, [180], [0, 180]),  # histogram of hue channel of postion of player
                color  # frame color
            ])

        return players

    def restart_capture(self):
        """
            Finds players controls on cam and parses them to mallets posiotions

        """
        res = self.findPlayers2()

        if res is not None:
            circles, frame = res
            self.players = self.parsePlayers(circles, frame)

    def getNewPositions(self):
        """

        :rtype : (p1_data((x,y),(vx,vy)), p2_data((x,y),(vx,vy))
        """
        frame = self.getFrame()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # result
        res = []
        i = 0
        for p in self.players:
            if p[0].count(0) != len(p[0]):
                # find new position of object
                dst = cv2.calcBackProject([hsv], [0], p[1], [0, 180], 1)
                r, p[0] = cv2.meanShift(dst, p[0], self.term_crit)
                x, y, w, h = p[0]
                cv2.rectangle(frame, (x, y), (x + w, y + h), p[2], 2)
            else:
                x, y, w, h = p[0]
                cv2.rectangle(frame, (x, y), (x + w, y + h), p[2], 2)

            p2 = p[0]
            pos = (p2[0] + p2[2] / 2.0, p2[1] + p2[3] / 2.0)
            res.append((
                pos,
                (pos[0] - self.oldPos[i][0], pos[1] - self.oldPos[i][1])  # calc velocity
            ))

            self.oldPos[i] = pos
            i += 1

        cv2.imshow(self.camWindow, frame)
        key = cv2.waitKey(10) & 0xFF
        if key == ord('r'):
            pl = self.findPlayers2()

            if pl is not None:
                circles, frame = pl
                self.players = self.parsePlayers(circles, frame)

        return res

    def stop_capture(self):
        self.cap.release()
        cv2.destroyAllWindows()
