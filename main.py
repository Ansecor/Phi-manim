from manim import *
from manim_slides import Slide
import numpy as np


class MovingCameraSlide(Slide, MovingCameraScene):
    pass


class Root3Base(MovingCameraSlide):
    BORDER = GREY_B
    OUTER_BORDER = 2.0
    INNER_BORDER = 1.0
    SMALLEST_BORDER = 0.7

    LABEL_SCALE = 0.18
    LABEL_MIN_SCALE = 0.07
    LABEL_POWER = 0.62
    TILE_FILL = GREY_E
    TILE_FILL_OPACITY = 0.05

    TARGET_BLUE = BLUE_E
    TARGET_BLUE_FILL = 0.22

    LABEL_COLORS = [
        RED_C,
        ORANGE,
        YELLOW_C,
        GREEN_C,
        TEAL_C,
        BLUE_C,
        PURPLE_C,
        PINK,
    ]

    def frame_for(self, mob, margin=1.12):
        width = max(mob.width, mob.height) * margin
        return mob.get_center(), width

    def rect_width(self, rect):
        x0, y0, x1, y1 = rect
        return x1 - x0

    def rect_height(self, rect):
        x0, y0, x1, y1 = rect
        return y1 - y0

    def make_square(self, rect, stroke_width=None, fill_color=None, fill_opacity=None, stroke_color=None):
        if stroke_width is None:
            stroke_width = self.INNER_BORDER
        if fill_color is None:
            fill_color = self.TILE_FILL
        if fill_opacity is None:
            fill_opacity = self.TILE_FILL_OPACITY
        if stroke_color is None:
            stroke_color = self.BORDER

        x0, y0, x1, y1 = rect
        s = min(x1 - x0, y1 - y0)

        sq = Square(side_length=float(s))
        sq.move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
        sq.set_stroke(stroke_color, stroke_width)
        sq.set_fill(fill_color, fill_opacity)
        return sq

    def make_outer(self, rect, stroke_width=None, stroke_color=None):
        if stroke_width is None:
            stroke_width = self.OUTER_BORDER
        if stroke_color is None:
            stroke_color = self.BORDER

        x0, y0, x1, y1 = rect
        r = Rectangle(width=float(x1 - x0), height=float(y1 - y0))
        r.move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
        r.set_stroke(stroke_color, stroke_width)
        return r

    def side_midpoint(self, rect, side):
        x0, y0, x1, y1 = rect
        if side == "LEFT":
            return np.array([x1, (y0 + y1) / 2, 0])
        if side == "RIGHT":
            return np.array([x0, (y0 + y1) / 2, 0])
        if side == "UP":
            return np.array([(x0 + x1) / 2, y0, 0])
        return np.array([(x0 + x1) / 2, y1, 0])

    def linear_expr_tex(self, a, b):
        # Prefer the positive-leading term first, matching forms like
        # x-y, 2y-x, 7y-4x, 11x-19y, 26y-15x, ...
        if a == 0 and b == 0:
            return "0"

        terms = []
        if a > 0:
            terms.append(("x", a))
        if b > 0:
            terms.append(("y", b))
        if a < 0:
            terms.append(("x", a))
        if b < 0:
            terms.append(("y", b))

        # If a negative term came first because no positive terms exist, swap by abs size for readability.
        if len(terms) == 2 and terms[0][1] < 0 and terms[1][1] > 0:
            terms = [terms[1], terms[0]]

        out = ""
        for idx, (var, coeff) in enumerate(terms):
            mag = abs(coeff)
            piece = var if mag == 1 else f"{mag}{var}"
            if idx == 0:
                out += piece if coeff > 0 else f"-{piece}"
            else:
                out += f"+{piece}" if coeff > 0 else f"-{piece}"
        return out

    def square_expression_sequence(self, n=40):
        root3 = np.sqrt(3)
        width_num = root3
        height_num = 1.0
        width_expr = (1, 0)
        height_expr = (0, 1)
        seq = []

        while len(seq) < n:
            if width_num >= height_num:
                q = int(width_num / height_num + 1e-9)
                for _ in range(q):
                    seq.append(height_expr)
                    if len(seq) >= n:
                        break
                width_expr = (
                    width_expr[0] - q * height_expr[0],
                    width_expr[1] - q * height_expr[1],
                )
                width_num -= q * height_num
            else:
                q = int(height_num / width_num + 1e-9)
                for _ in range(q):
                    seq.append(width_expr)
                    if len(seq) >= n:
                        break
                height_expr = (
                    height_expr[0] - q * width_expr[0],
                    height_expr[1] - q * width_expr[1],
                )
                height_num -= q * width_num

        return [self.linear_expr_tex(a, b) for a, b in seq]

    def outer_width_sequence(self, n=8):
        # Widths of the repeated smaller rectangles across successive zooms.
        root3 = np.sqrt(3)
        width_num = root3
        height_num = 1.0
        width_expr = (1, 0)
        height_expr = (0, 1)
        out = []
        while len(out) < n:
            if width_num >= height_num:
                q = int(width_num / height_num + 1e-9)
                width_expr = (
                    width_expr[0] - q * height_expr[0],
                    width_expr[1] - q * height_expr[1],
                )
                width_num -= q * height_num
                out.append(self.linear_expr_tex(*width_expr))
            else:
                q = int(height_num / width_num + 1e-9)
                height_expr = (
                    height_expr[0] - q * width_expr[0],
                    height_expr[1] - q * width_expr[1],
                )
                height_num -= q * width_num
        return out

    def expr_label_for(self, rect, side, expr, color, base_side=None, buff_scale=0.018):
        txt = MathTex(expr)

        x0, y0, x1, y1 = rect
        side_len = min(x1 - x0, y1 - y0)
        if base_side is None:
            base_side = side_len

        size_ratio = side_len / base_side if base_side > 0 else 1.0
        label_scale = self.LABEL_SCALE * (size_ratio ** self.LABEL_POWER)
        label_scale = max(self.LABEL_MIN_SCALE, min(self.LABEL_SCALE, label_scale))
        txt.scale(label_scale)
        txt.set_color(color)
        txt.set_stroke(BLACK, width=1.2, opacity=0.35)

        anchor = self.side_midpoint(rect, side)
        buff = max(0.008, min(0.03, buff_scale * (size_ratio ** 0.85)))

        if side == "LEFT":
            txt.rotate(PI / 2)
            txt.next_to(anchor, RIGHT, buff=buff)
        elif side == "RIGHT":
            txt.rotate(PI / 2)
            txt.next_to(anchor, LEFT, buff=buff)
        elif side == "UP":
            txt.next_to(anchor, DOWN, buff=buff)
        elif side == "DOWN":
            txt.next_to(anchor, UP, buff=buff)
        return txt

    def top_label_for_rect(self, rect, expr, color=WHITE, scale=0.24, buff=0.06):
        mob = MathTex(expr)
        mob.scale(scale)
        mob.set_color(color)
        mob.set_stroke(BLACK, width=1.2, opacity=0.35)
        x0, y0, x1, y1 = rect
        mob.next_to(np.array([(x0 + x1) / 2, y1, 0]), UP, buff=buff)
        return mob

    def side_label_for_rect(self, rect, expr, color=WHITE, scale=0.24, buff=0.06):
        mob = MathTex(expr)
        mob.scale(scale)
        mob.rotate(PI / 2)
        mob.set_color(color)
        mob.set_stroke(BLACK, width=1.2, opacity=0.35)
        x0, y0, x1, y1 = rect
        mob.next_to(np.array([x0, (y0 + y1) / 2, 0]), LEFT, buff=buff)
        return mob

    def subdivide(self, remainder, side):
        x0, y0, x1, y1 = remainder
        w = x1 - x0
        h = y1 - y0
        eps = 1e-9

        if w >= h:
            s = h
            q = int((w / h) + eps)

            if side == "LEFT":
                squares = [(x0 + i * s, y0, x0 + (i + 1) * s, y0 + s) for i in range(q)]
                remainder = (x0 + q * s, y0, x1, y1)
            else:
                squares = [(x1 - (i + 1) * s, y0, x1 - i * s, y0 + s) for i in range(q)]
                remainder = (x0, y0, x1 - q * s, y1)
        else:
            s = w
            q = int((h / w) + eps)

            if side == "UP":
                squares = [(x0, y1 - (i + 1) * s, x0 + s, y1 - i * s) for i in range(q)]
                remainder = (x0, y0, x1, y1 - q * s)
            else:
                squares = [(x0, y0 + i * s, x0 + s, y0 + (i + 1) * s) for i in range(q)]
                remainder = (x0, y0 + q * s, x1, y1)

        return squares, remainder

    def build_tiles(self, n=8):
        root3 = np.sqrt(3)
        outer = (0.0, 0.0, root3, 1.0)
        remainder = outer
        cycle = ["LEFT", "UP", "RIGHT", "DOWN"]

        tiles = []
        k = 0

        while len(tiles) < n:
            side = cycle[k % 4]
            sqs, remainder = self.subdivide(remainder, side)

            for s in sqs:
                tiles.append({"rect": s, "side": side})
                if len(tiles) >= n:
                    break
            k += 1

        all_rects = [t["rect"] for t in tiles] + [outer]
        xs = [x for r in all_rects for x in (r[0], r[2])]
        ys = [y for r in all_rects for y in (r[1], r[3])]

        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2

        def shift(r):
            x0, y0, x1, y1 = r
            return (x0 - cx, y0 - cy, x1 - cx, y1 - cy)

        outer = shift(outer)
        for t in tiles:
            t["rect"] = shift(t["rect"])

        return outer, tiles

    def fit_root3_rect_in_square(self, square_rect, horizontal=True, fill_fraction=0.90):
        sx0, sy0, sx1, sy1 = square_rect
        sw = sx1 - sx0
        sh = sy1 - sy0
        cx = (sx0 + sx1) / 2
        cy = (sy0 + sy1) / 2
        root3 = np.sqrt(3)

        if horizontal:
            h = min(sh, sw / root3) * fill_fraction
            w = root3 * h
        else:
            w = min(sw, sh / root3) * fill_fraction
            h = root3 * w

        return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

    def build_scaled_copy_from_rect(self, source_outer_rect, source_tiles, target_outer_rect):
        ox0, oy0, ox1, oy1 = source_outer_rect
        tx0, ty0, tx1, ty1 = target_outer_rect

        ow = ox1 - ox0
        oh = oy1 - oy0
        tw = tx1 - tx0
        th = ty1 - ty0

        sx = tw / ow
        sy = th / oh

        scaled_tiles = []
        for t in source_tiles:
            x0, y0, x1, y1 = t["rect"]
            nx0 = tx0 + (x0 - ox0) * sx
            ny0 = ty0 + (y0 - oy0) * sy
            nx1 = tx0 + (x1 - ox0) * sx
            ny1 = ty0 + (y1 - oy0) * sy
            scaled_tiles.append({"rect": (nx0, ny0, nx1, ny1), "side": t["side"]})
        return scaled_tiles

    def build_intro_math_group(self):
        title = Tex(r"The smaller rectangle has the same ratio.")
        title.scale(0.10)

        line0 = MathTex(r"\frac{2x-3y}{2y-x}")
        line1 = MathTex(r"\frac{2(x/y)-3}{2-(x/y)}")
        line2 = MathTex(r"\frac{2\sqrt{3}-3}{2-\sqrt{3}}")
        line3 = MathTex(r"\frac{2\sqrt{3}-3}{2-\sqrt{3}}\cdot\frac{2+\sqrt{3}}{2+\sqrt{3}}")
        line4 = MathTex(r"\frac{4\sqrt{3}+6-6-3\sqrt{3}}{1}")
        line5 = MathTex(r"\sqrt{3}")

        for mob in (line0, line1, line2, line3, line4, line5):
            mob.scale(0.50)

        group = VGroup(title, line0)
        group.arrange(DOWN, buff=0.18)
        return title, [line0, line1, line2, line3, line4, line5]

    def build_final_panel(self, color, final_expr):
        lines = VGroup(
            MathTex(rf"0<{final_expr}<1"),
            Tex(rf"But {final_expr} is a positive integer combination of $x$ and $y$."),
            MathTex(r"\frac{x}{y}\ne\sqrt{3}"),
            MathTex(r"\text{Q.E.D.}")
        )
        lines[0].scale(0.50)
        lines[1].scale(0.28)
        lines[2].scale(0.56)
        lines[3].scale(0.56)
        lines[2].set_color(color)
        lines[3].set_color(color)
        lines.arrange(DOWN, buff=0.18)
        return lines

    def recursive_zoom_scene(self, *, start_color, next_color, scene_expr, next_scene_expr, final_scene=False):
        outer_rect, tiles = self.build_tiles(8)
        exprs = self.square_expression_sequence(24)

        root3 = np.sqrt(3)
        handoff_height = 4.0
        handoff_width = root3 * handoff_height
        handoff_rect = (
            -handoff_width / 2,
            -handoff_height / 2,
            handoff_width / 2,
            handoff_height / 2,
        )

        current_rect = self.make_outer(handoff_rect, stroke_width=0.9, stroke_color=start_color)
        current_rect.set_fill(start_color, 0.28)
        top_expr_label = self.top_label_for_rect(handoff_rect, scene_expr, color=start_color, scale=0.20, buff=0.03)

        c, w = self.frame_for(VGroup(current_rect, top_expr_label), 1.16)
        self.camera.frame.move_to(c)
        self.camera.frame.set_width(w)
        self.add(current_rect, top_expr_label)

        scaled_tiles = self.build_scaled_copy_from_rect(outer_rect, tiles, handoff_rect)
        geom_squares = VGroup()
        geom_labels = VGroup()
        base_side = min(
            scaled_tiles[0]["rect"][2] - scaled_tiles[0]["rect"][0],
            scaled_tiles[0]["rect"][3] - scaled_tiles[0]["rect"][1],
        )

        for i, t in enumerate(scaled_tiles):
            stroke = self.SMALLEST_BORDER if i == len(scaled_tiles) - 1 else self.INNER_BORDER
            geom_squares.add(self.make_square(t["rect"], stroke_width=stroke))
            geom_labels.add(
                self.expr_label_for(
                    t["rect"],
                    t["side"],
                    exprs[i],
                    self.LABEL_COLORS[i % len(self.LABEL_COLORS)],
                    base_side=base_side,
                )
            )

        self.play(
            current_rect.animate.set_fill(start_color, 0.06).set_stroke(start_color, 0.5),
            LaggedStart(*[FadeIn(sq) for sq in geom_squares], lag_ratio=0.08),
            run_time=1.2,
        )
        self.play(LaggedStart(*[FadeIn(lb) for lb in geom_labels], lag_ratio=0.045), run_time=0.95)
        self.next_slide()

        self.play(geom_labels.animate.set_opacity(0.16), run_time=0.25)

        selected_square_rect = scaled_tiles[-1]["rect"]
        next_rect_coords = self.fit_root3_rect_in_square(selected_square_rect, horizontal=True, fill_fraction=0.90)
        next_rect = self.make_outer(next_rect_coords, stroke_width=0.9, stroke_color=next_color)
        next_rect.set_fill(next_color, 0.42)
        next_top_label = self.top_label_for_rect(next_rect_coords, next_scene_expr, color=next_color, scale=0.18, buff=0.025)

        background_group = VGroup(current_rect, top_expr_label, geom_squares[:-1])

        self.play(
            background_group.animate.set_opacity(0.18),
            geom_squares[-1].animate.set_stroke(width=0.0).set_fill(opacity=0.0),
            FadeIn(next_rect),
            FadeIn(next_top_label),
            run_time=0.7,
        )

        zoom_center, zoom_width = self.frame_for(VGroup(next_rect, next_top_label), 1.08)
        self.play(
            self.camera.frame.animate.move_to(zoom_center).set_width(zoom_width),
            run_time=2.4,
            rate_func=smooth,
        )
        self.next_slide()

        if final_scene:
            final_center, final_width = self.frame_for(VGroup(next_rect, next_top_label), 1.10)
            self.play(
                self.camera.frame.animate.move_to(final_center).set_width(final_width),
                run_time=0.9,
            )
            self.wait(0.4)
            self.next_slide()


class Root3RatioIntro(Root3Base):
    def construct(self):
        lead = Tex(r"Let")
        lead.scale(0.70)

        ratio = MathTex(r"\frac{x}{y}=\sqrt{3}")
        ratio.scale(0.92)

        statement = VGroup(lead, ratio)
        statement.arrange(RIGHT, buff=0.20)
        statement.move_to(0.12 * UP)

        subtitle = Tex(r"We will show this same ratio reappears after each zoom.")
        subtitle.scale(0.34)
        subtitle.next_to(statement, DOWN, buff=0.20)

        frame_group = VGroup(statement, subtitle)
        c, w = self.frame_for(frame_group, 1.18)
        self.camera.frame.move_to(c)
        self.camera.frame.set_width(w)

        self.play(FadeIn(lead, shift=0.12 * LEFT), Write(ratio), run_time=1.0)
        self.next_slide()
        self.play(FadeIn(subtitle, shift=0.12 * DOWN), run_time=0.8)
        self.next_slide()


class Root3SpiralIntro(Root3Base):
    def construct(self):
        outer_rect, tiles = self.build_tiles(8)
        outer = self.make_outer(outer_rect)

        # Hardcoded to match the pattern the user specified.
        tile_exprs = [
            "y",
            "x-y",
            "2y-x",
            "2y-x",
            "3x-5y",
            "7y-4x",
            "7y-4x",
            "11x-19y",
        ]

        squares = VGroup()
        labels = VGroup()
        base_side = min(
            tiles[0]["rect"][2] - tiles[0]["rect"][0],
            tiles[0]["rect"][3] - tiles[0]["rect"][1],
        )

        for i, t in enumerate(tiles):
            stroke = self.SMALLEST_BORDER if i == len(tiles) - 1 else self.INNER_BORDER
            squares.add(self.make_square(t["rect"], stroke_width=stroke))
            labels.add(
                self.expr_label_for(
                    t["rect"],
                    t["side"],
                    tile_exprs[i],
                    self.LABEL_COLORS[i % len(self.LABEL_COLORS)],
                    base_side=base_side,
                )
            )

        outer_width_label = self.top_label_for_rect(outer_rect, "x", color=WHITE, scale=0.26, buff=0.05)
        outer_height_label = self.side_label_for_rect(outer_rect, "y", color=WHITE, scale=0.26, buff=0.05)

        built = VGroup()
        built_labels = VGroup()

        self.add(outer, outer_width_label, outer_height_label, built, built_labels)
        built.add(squares[0])
        built_labels.add(labels[0])

        c, w = self.frame_for(VGroup(outer, outer_width_label, outer_height_label, squares[0]), 1.18)
        self.camera.frame.move_to(c)
        self.camera.frame.set_width(w)

        self.play(
            Create(outer),
            FadeIn(outer_width_label),
            FadeIn(outer_height_label),
            FadeIn(built[0]),
            FadeIn(built_labels[0]),
            run_time=1.0,
        )
        self.next_slide()

        for i in range(1, len(squares)):
            new_sq = squares[i]
            new_lab = labels[i]
            preview = VGroup(outer, built, new_sq, outer_width_label, outer_height_label)
            c, w = self.frame_for(preview, 1.14)

            self.play(
                self.camera.frame.animate.move_to(c).set_width(w),
                FadeIn(new_sq),
                FadeIn(new_lab),
                run_time=0.75,
            )
            built.add(new_sq)
            built_labels.add(new_lab)
            self.next_slide()

        self.play(built_labels.animate.set_opacity(0.12), run_time=0.25)

        # Centered yellow ratio computation before the blue zoom.
        title = Tex(r"The smaller rectangle has the same ratio.", color=YELLOW)
        title.scale(0.34)
        title.move_to(outer.get_center() + 0.66 * UP)
        title.set_stroke(BLACK, width=1.0, opacity=0.30)
        title.set_z_index(5)

        line0 = MathTex(r"\frac{2x-3y}{2y-x}", color=YELLOW)
        line1 = MathTex(r"\frac{2(x/y)-3}{2-(x/y)}", color=YELLOW)
        line2 = MathTex(r"\frac{2\sqrt{3}-3}{2-\sqrt{3}}", color=YELLOW)
        line3 = MathTex(r"\frac{2\sqrt{3}-3}{2-\sqrt{3}}\cdot\frac{2+\sqrt{3}}{2+\sqrt{3}}", color=YELLOW)
        line4 = MathTex(r"\frac{4\sqrt{3}+6-6-3\sqrt{3}}{1}", color=YELLOW)
        line5 = MathTex(r"=\sqrt{3}", color=YELLOW)
        math_lines = [line0, line1, line2, line3, line4, line5]
        equation_center = outer.get_center() + 0.02 * DOWN
        for mob in math_lines:
            mob.scale(0.50)
            mob.move_to(equation_center)
            mob.set_z_index(5)
            mob.set_stroke(BLACK, width=1.2, opacity=0.35)

        current = line0
        message = Tex(r"So the blue rectangle is again a $\sqrt{3}$ rectangle.", color=YELLOW)
        message.scale(0.30)
        message.move_to(outer.get_center() + 0.92 * DOWN)
        message.set_stroke(BLACK, width=1.0, opacity=0.30)
        message.set_z_index(5)

        self.play(
            FadeIn(title, shift=0.10 * DOWN),
            Write(current),
            run_time=0.95,
        )
        self.next_slide()

        for new in math_lines[1:]:
            new.move_to(current)
            self.play(TransformMatchingTex(current, new), run_time=0.9)
            current = new
            self.next_slide()

        self.play(FadeIn(message, shift=0.10 * UP), run_time=0.6)
        self.next_slide()
        self.play(FadeOut(VGroup(title, current, message)), run_time=0.45)

        selected_square_rect = tiles[-1]["rect"]
        handoff_rect = self.fit_root3_rect_in_square(selected_square_rect, horizontal=True, fill_fraction=0.90)

        handoff_fill = self.make_outer(handoff_rect, stroke_width=0.9, stroke_color=self.TARGET_BLUE)
        handoff_fill.set_fill(self.TARGET_BLUE, 0.40)
        handoff_label = self.top_label_for_rect(handoff_rect, "11x-19y", color=self.TARGET_BLUE, scale=0.18, buff=0.025)

        background_group = VGroup(outer, outer_width_label, outer_height_label, built[:-1], built_labels)

        self.play(
            background_group.animate.set_opacity(0.18),
            built[-1].animate.set_stroke(width=0.0).set_fill(opacity=0.0),
            FadeIn(handoff_fill),
            FadeIn(handoff_label),
            run_time=0.7,
        )

        zoom_center, zoom_width = self.frame_for(VGroup(handoff_fill, handoff_label), 1.08)
        self.play(
            self.camera.frame.animate.move_to(zoom_center).set_width(zoom_width),
            run_time=2.6,
            rate_func=smooth,
        )
        self.next_slide()


class Root3AlgebraInterstitial(Root3Base):
    def construct(self):
        title, forms = self.build_intro_math_group()
        title.scale(0.94)
        title.set_color(BLUE_B)

        forms_group = VGroup(*forms)
        forms_group.arrange(DOWN, buff=0.20, aligned_edge=ORIGIN)

        group = VGroup(title, forms_group)
        group.arrange(DOWN, buff=0.28)
        group.move_to(0.55 * DOWN)

        c, w = self.frame_for(group, 1.14)
        self.camera.frame.move_to(c)
        self.camera.frame.set_width(w)

        current = forms[0]
        self.play(FadeIn(title, shift=0.12 * UP), Write(current), run_time=1.0)
        self.next_slide()

        for new in forms[1:]:
            new.move_to(current)
            self.play(TransformMatchingTex(current, new), run_time=0.95)
            current = new
            self.next_slide()


class Root3QEDInterstitial(Root3Base):
    def construct(self):
        final_expr = "153x-265y"
        title = Tex(r"Eventually the smaller width is less than 1.")
        title.scale(0.44)
        title.set_color(ORANGE)

        panel = self.build_final_panel(ORANGE, final_expr)
        group = VGroup(title, panel)
        group.arrange(DOWN, buff=0.28)
        group.move_to(ORIGIN)

        c, w = self.frame_for(group, 1.18)
        self.camera.frame.move_to(c)
        self.camera.frame.set_width(w)

        self.play(FadeIn(title, shift=0.10 * UP), run_time=0.7)
        self.next_slide()
        self.play(FadeIn(panel[0], shift=0.08 * UP), run_time=0.7)
        self.next_slide()
        self.play(FadeIn(panel[1], shift=0.08 * UP), run_time=0.7)
        self.next_slide()
        self.play(Write(panel[2]), run_time=0.8)
        self.next_slide()
        self.play(Write(panel[3]), run_time=0.8)
        self.next_slide()


class Root3ZoomScene(Root3Base):
    def construct(self):
        self.recursive_zoom_scene(
            start_color=BLUE_E,
            next_color=GREEN_E,
            scene_expr="11x-19y",
            next_scene_expr="26y-15x",
            final_scene=False,
        )


class Root3ZoomScene2(Root3Base):
    def construct(self):
        self.recursive_zoom_scene(
            start_color=GREEN_E,
            next_color=YELLOW_E,
            scene_expr="26y-15x",
            next_scene_expr="41x-71y",
            final_scene=False,
        )


class Root3ZoomScene3(Root3Base):
    def construct(self):
        self.recursive_zoom_scene(
            start_color=YELLOW_E,
            next_color=GOLD_E,
            scene_expr="41x-71y",
            next_scene_expr="97y-56x",
            final_scene=False,
        )


class Root3ZoomScene4(Root3Base):
    def construct(self):
        self.recursive_zoom_scene(
            start_color=GOLD_E,
            next_color=ORANGE,
            scene_expr="97y-56x",
            next_scene_expr="153x-265y",
            final_scene=True,
        )