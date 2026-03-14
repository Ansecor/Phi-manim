from manim import *
from manim_slides import Slide
import numpy as np


class FibSlide(Slide, MovingCameraScene):
    pass


class FibBase(FibSlide):
    LABEL_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, TEAL]
    FLASH_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, TEAL]

    def fibonacci(self, n: int):
        f = [1, 1]
        while len(f) < n:
            f.append(f[-1] + f[-2])
        return f[:n]

    def build_tiles(self, n_tiles: int):
        fibs = self.fibonacci(n_tiles)

        rects = [(0, 0, 1, 1)]
        if n_tiles >= 2:
            rects.append((1, 0, 2, 1))

        min_x, min_y = 0, 0
        max_x, max_y = 2, 1
        directions = ["UP", "LEFT", "DOWN", "RIGHT"]

        for i in range(2, n_tiles):
            s = fibs[i]
            d = directions[(i - 2) % 4]

            if d == "UP":
                rect = (min_x, max_y, max_x, max_y + s)
                max_y += s
            elif d == "LEFT":
                rect = (min_x - s, min_y, min_x, max_y)
                min_x -= s
            elif d == "DOWN":
                rect = (min_x, min_y - s, max_x, min_y)
                min_y -= s
            else:  # RIGHT
                rect = (max_x, min_y, max_x + s, max_y)
                max_x += s

            rects.append(rect)

        shifted = []
        for x0, y0, x1, y1 in rects:
            shifted.append((x0 - 0.5, y0 - 0.5, x1 - 0.5, y1 - 0.5))

        return shifted

    def make_square(self, rect, color=YELLOW, stroke_width=3):
        x0, y0, x1, y1 = rect
        side = x1 - x0

        sq = Square(side_length=side)
        sq.move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
        sq.set_stroke(color, stroke_width)
        return sq

    def corners(self, rect):
        x0, y0, x1, y1 = rect
        return {
            "BL": np.array([x0, y0, 0.0]),
            "BR": np.array([x1, y0, 0.0]),
            "TR": np.array([x1, y1, 0.0]),
            "TL": np.array([x0, y1, 0.0]),
            "C": np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0.0]),
        }

    def make_arc_spiral_oriented(self, rect, index, n_tiles, stroke_width=8):
        c = self.corners(rect)
        reverse_index = n_tiles - 1 - index

        start = c["BL"]
        end = c["TR"]
        base_angle = -PI / 2

        arc = ArcBetweenPoints(start, end, angle=base_angle)
        arc.set_stroke(GOLD, stroke_width)

        k = reverse_index % 4
        arc.rotate(-k * PI / 2, about_point=c["C"])
        return arc

    def frame_for(self, mob, margin=1.12):
        width = max(mob.width, mob.height) * margin
        center = mob.get_center()
        return center, width

    def rotate_to_horizontal(self, mob):
        if mob.width >= mob.height:
            return mob.copy(), 0
        rotated = mob.copy().rotate(-PI / 2, about_point=ORIGIN)
        return rotated, -PI / 2

    def square_label(self, rect, index):
        x0, y0, x1, y1 = rect
        side = x1 - x0
        color = self.LABEL_COLORS[index % len(self.LABEL_COLORS)]

        # Ratio carried by successive Fibonacci squares
        label = MathTex(
            rf"\frac{{F_{{{index+2}}}}}{{F_{{{index+1}}}}}",
            color=color,
        )

        scale = np.clip(0.12 + 0.10 * side, 0.22, 0.60)
        label.scale(scale)

        center = np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0])
        label.move_to(center)
        return label


class FibRatioIntro(FibBase):
    def construct(self):
        line1 = Text("Let", font_size=38)
        line2 = MathTex(r"\frac{x}{y} = \frac{F_{n+1}}{F_n}", color=YELLOW).scale(1.2)
        line3 = Text("for n \u2265 1", font_size=30, color=YELLOW)
        line4 = MathTex(r"\frac{F_{n+1}}{F_n} \to \varphi", color=YELLOW).scale(1.0)

        block = VGroup(line1, line2, line3, line4).arrange(DOWN, buff=0.35)
        block.move_to(ORIGIN)

        self.play(FadeIn(line1), Write(line2), run_time=1.2)
        self.next_slide()
        self.play(FadeIn(line3), FadeIn(line4), run_time=1.0)
        self.next_slide()
        self.wait(0.5)


class FibonacciDrosteSpiral(FibBase):
    def construct(self):
        n_tiles = 12
        spiral_stroke_width = 8

        rects = self.build_tiles(n_tiles)
        square_templates = [self.make_square(r) for r in rects]
        label_templates = [self.square_label(r, i) for i, r in enumerate(rects)]
        arc_templates = [
            self.make_arc_spiral_oriented(rects[i], i, n_tiles, stroke_width=spiral_stroke_width)
            for i in range(n_tiles)
        ]

        squares = VGroup()
        labels = VGroup()
        self.add(squares, labels)

        squares.add(square_templates[0].copy())
        labels.add(label_templates[0].copy())

        center, width = self.frame_for(VGroup(squares, labels), margin=1.9)
        self.camera.frame.move_to(center)
        self.camera.frame.set_width(width)

        self.play(FadeIn(squares[0]), FadeIn(labels[0]), run_time=0.8)
        self.next_slide()

        # Build the tiling square-by-square with one input per step.
        for i in range(1, n_tiles):
            new_square = square_templates[i].copy()
            new_label = label_templates[i].copy()

            preview_squares = squares.copy()
            preview_labels = labels.copy()
            preview_squares.add(new_square)
            preview_labels.add(new_label)
            preview = VGroup(preview_squares, preview_labels)

            target_center, target_width = self.frame_for(preview, margin=1.18)

            self.play(
                Create(new_square),
                FadeIn(new_label),
                self.camera.frame.animate.move_to(target_center).set_width(target_width),
                run_time=0.9,
                rate_func=smooth,
            )

            squares.add(new_square)
            labels.add(new_label)
            self.next_slide()

        horizontal_preview, needed_rotation = self.rotate_to_horizontal(VGroup(squares, labels))
        if needed_rotation != 0:
            target_center, target_width = self.frame_for(horizontal_preview, margin=1.15)
            self.play(
                Rotate(squares, angle=needed_rotation, about_point=ORIGIN),
                Rotate(labels, angle=needed_rotation, about_point=ORIGIN),
                self.camera.frame.animate.move_to(target_center).set_width(target_width),
                run_time=1.2,
                rate_func=smooth,
            )
            self.next_slide()

        spiral = VGroup(*[arc.copy() for arc in arc_templates])
        if needed_rotation != 0:
            spiral.rotate(needed_rotation, about_point=ORIGIN)

        self.play(Create(spiral), run_time=2.8, rate_func=linear)
        self.next_slide()

        # Flash each self-similar square largest -> smallest in different colors.
        flash_anims = []
        ordered_squares = list(squares)[::-1]  # largest to smallest
        for i, sq in enumerate(ordered_squares):
            color = self.FLASH_COLORS[i % len(self.FLASH_COLORS)]
            flash_anims.append(
                sq.animate.set_stroke(color=color, width=5)
            )
        self.play(LaggedStart(*flash_anims, lag_ratio=0.18), run_time=3.0)
        self.next_slide()

        # Zoom back to the smallest square so its small text is readable.
        smallest_square = squares[0]
        smallest_label = labels[0]
        focus_group = VGroup(smallest_square, smallest_label)
        focus_center, focus_width = self.frame_for(focus_group, margin=6.0)
        self.play(
            self.camera.frame.animate.move_to(focus_center).set_width(focus_width),
            run_time=2.0,
            rate_func=smooth,
        )
        self.next_slide()

        final_text = Text(
            "The golden ratio is not the ratio of two integers",
            font_size=30,
            color=YELLOW,
        )
        final_eq = MathTex(r"\varphi \neq \frac{x}{y}", color=YELLOW).scale(1.2)
        final_eq2 = MathTex(
            r"\varphi \neq \frac{m}{n}\qquad (m,n\in\mathbb{Z},\ n\neq 0)",
            color=YELLOW,
        ).scale(0.95)

        final_group = VGroup(final_text, final_eq).arrange(DOWN, buff=0.35)
        final_group.move_to(ORIGIN)

        self.play(FadeIn(final_text), Write(final_eq), run_time=1.2)
        self.next_slide()
        self.play(TransformMatchingTex(final_eq, final_eq2), run_time=1.2)
        self.next_slide()
        self.wait(0.5)