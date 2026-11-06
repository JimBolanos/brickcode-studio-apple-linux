/* The four bricks, drawn with Cairo.
 *
 * Drawn from photographs of the real hardware, not from memory:
 *   RCX   - yellow, portrait. Grey input pads (1 2 3) above, black output
 *           pads (A B C) below, View / Prgm on the upper row and the red
 *           On-Off and green Run on the lower one.
 *   Scout - blue, portrait. Yellow stud pads 1 and 2, the light sensor
 *           barrel on top, Select / Change over the menu LCD, On-Off / Run
 *           under it, black A and B pads at the foot with the arrow keys
 *           between them.
 *   NXT   - white, portrait. Dark port strips top (A B C, USB) and bottom
 *           (1 2 3 4), the orange enter button between two grey arrows, the
 *           back button below it and the speaker grille on the right.
 *   EV3   - white and grey, portrait. The screen in a black window up in the
 *           grey bezel, four tabs on the LCD, then the cluster of buttons:
 *           up and down as one octagon, a pill either side and a square in
 *           the middle, lit red from underneath. Grey foot with the name.
 *           Drawn from a photograph for the proportions only; there is no
 *           logo on it, the LEGO one is not ours to draw.
 *
 * Cairo rather than SVG on purpose: loading SVG into GTK4 would mean
 * librsvg as a new dependency on both Linux and macOS, and this program
 * carries none it does not need.
 */

static void bk_hex(cairo_t *cr, const char *hex) {
    unsigned int r = 0, g = 0, b = 0;
    sscanf(hex + (hex[0] == '#' ? 1 : 0), "%02x%02x%02x", &r, &g, &b);
    cairo_set_source_rgb(cr, r / 255.0, g / 255.0, b / 255.0);
}

static void bk_rrect(cairo_t *cr, double x, double y, double w, double h, double r) {
    cairo_new_path(cr);
    if (r > w / 2) r = w / 2;
    if (r > h / 2) r = h / 2;
    cairo_new_sub_path(cr);
    cairo_arc(cr, x + w - r, y + r,     r, -G_PI / 2, 0);
    cairo_arc(cr, x + w - r, y + h - r, r, 0,          G_PI / 2);
    cairo_arc(cr, x + r,     y + h - r, r, G_PI / 2,   G_PI);
    cairo_arc(cr, x + r,     y + r,     r, G_PI,       3 * G_PI / 2);
    cairo_close_path(cr);
}

static void bk_fill(cairo_t *cr, const char *hex,
                    double x, double y, double w, double h, double r) {
    bk_hex(cr, hex);
    bk_rrect(cr, x, y, w, h, r);
    cairo_fill(cr);
}

static void bk_dot(cairo_t *cr, const char *hex, double cx, double cy, double r) {
    bk_hex(cr, hex);
    cairo_new_path(cr);
    cairo_arc(cr, cx, cy, r, 0, 2 * G_PI);
    cairo_fill(cr);
}

/* Text anchored at the left, or centred when centre is TRUE. */
static void bk_text(cairo_t *cr, const char *hex, double x, double y,
                    double size, gboolean bold, gboolean centre, const char *s) {
    cairo_text_extents_t e;
    bk_hex(cr, hex);
    cairo_select_font_face(cr, "sans-serif", CAIRO_FONT_SLANT_NORMAL,
                           bold ? CAIRO_FONT_WEIGHT_BOLD : CAIRO_FONT_WEIGHT_NORMAL);
    cairo_set_font_size(cr, size);
    if (centre) {
        cairo_text_extents(cr, s, &e);
        x -= e.width / 2 + e.x_bearing;
    }
    cairo_move_to(cr, x, y);
    cairo_show_text(cr, s);
}

/* How much of the card a brick takes up. Below 1.0 it sits in its own
 * breathing room instead of touching the edges. */
#define BK_SCALE 0.50

/* Fit a design-space box of dw x dh into the widget, centred. */
static void bk_begin(cairo_t *cr, int w, int h, double dw, double dh) {
    double s = MIN(w / dw, h / dh) * BK_SCALE;
    cairo_translate(cr, (w - dw * s) / 2, (h - dh * s) / 2);
    cairo_scale(cr, s, s);
}

/* The app's own icon, the same shapes as brickcode-studio.svg, drawn here
 * so the masthead needs neither librsvg nor an installed image file. */
static void bk_ellipse(cairo_t *cr, const char *hex,
                       double cx, double cy, double rx, double ry) {
    cairo_save(cr);
    cairo_new_path(cr);
    cairo_translate(cr, cx, cy);
    cairo_scale(cr, rx, ry);
    cairo_arc(cr, 0, 0, 1, 0, 2 * G_PI);
    cairo_restore(cr);
    bk_hex(cr, hex);
    cairo_fill(cr);
}

static void bk_draw_logo(cairo_t *cr, int w, int h) {
    cairo_save(cr);
    double s = MIN(w, h) / 512.0;
    cairo_translate(cr, (w - 512 * s) / 2, (h - 512 * s) / 2);
    cairo_scale(cr, s, s);

    cairo_pattern_t *g = cairo_pattern_create_linear(0, 0, 0, 512);
    cairo_pattern_add_color_stop_rgb(g, 0, 0x1C / 255.0, 0x2A / 255.0, 0x4A / 255.0);
    cairo_pattern_add_color_stop_rgb(g, 1, 0x12 / 255.0, 0x1A / 255.0, 0x30 / 255.0);
    bk_rrect(cr, 0, 0, 512, 512, 112.64);
    cairo_set_source(cr, g);
    cairo_fill(cr);
    cairo_pattern_destroy(g);

    bk_fill(cr, "#787E88", 66, 92, 380, 340, 44);
    bk_fill(cr, "#DEE2E8", 66, 84, 380, 336, 44);
    bk_fill(cr, "#F4F6FA", 80, 92, 352, 20, 10);
    bk_fill(cr, "#3C4048", 112, 128, 288, 138, 16);
    bk_fill(cr, "#96B08C", 122, 138, 268, 118, 10);

    bk_fill(cr, "#223422", 196, 170, 22, 22, 3);
    bk_fill(cr, "#223422", 296, 170, 22, 22, 3);
    bk_fill(cr, "#223422", 196, 214, 108, 12, 5);
    bk_fill(cr, "#223422", 184, 200, 16, 14, 5);
    bk_fill(cr, "#223422", 300, 200, 16, 14, 5);

    bk_fill(cr, "#464C58", 112, 292, 64, 48, 12);
    bk_fill(cr, "#464C58", 336, 292, 64, 48, 12);
    bk_fill(cr, "#464C58", 180, 362, 152, 30, 12);

    bk_ellipse(cr, "#FA8C14", 256, 316, 46, 34);
    bk_ellipse(cr, "#FFB046", 256, 310, 32, 18);

    bk_fill(cr, "#282C34", 112, 404, 52, 20, 6);
    bk_fill(cr, "#282C34", 176, 404, 52, 20, 6);
    bk_fill(cr, "#282C34", 240, 404, 52, 20, 6);
    bk_fill(cr, "#282C34", 304, 404, 52, 20, 6);

    cairo_restore(cr);
}

/* ------------------------------------------------------------------ RCX */
static void bk_draw_rcx(cairo_t *cr, int w, int h) {
    cairo_save(cr);
    bk_begin(cr, w, h, 210, 272);

    bk_fill(cr, "#C9A510", 6, 6, 198, 260, 13);      /* the edge below */
    bk_fill(cr, "#F4C81B", 6, 2, 198, 260, 13);      /* the yellow face */
    bk_fill(cr, "#1D1D1F", 74, 2, 62, 17, 4);        /* dark block on top */

    /* Three ports, not a grid. The brick has three inputs and three
     * outputs; the old drawing showed eight pads above and sixteen below,
     * which matched nothing on it and left the numbers labelling air. */
    bk_fill(cr, "#9A9A9A", 30, 26, 150, 46, 7);      /* inputs 1 2 3 */
    for (int port = 0; port < 3; port++)
        for (int row = 0; row < 2; row++)
            for (int col = 0; col < 2; col++)
                bk_fill(cr, "#C2C2C2", 34 + port * 54 + col * 18,
                        32 + row * 19, 16, 15, 2.5);

    bk_text(cr, "#1D1D1F", 27,  86, 11, TRUE, FALSE, "View");
    bk_text(cr, "#1D1D1F", 155, 86, 11, TRUE, FALSE, "Prgm");
    bk_text(cr, "#1D1D1F", 72,  87, 14, TRUE, TRUE,  "1");
    bk_text(cr, "#1D1D1F", 105, 87, 14, TRUE, TRUE,  "2");
    bk_text(cr, "#1D1D1F", 138, 87, 14, TRUE, TRUE,  "3");

    /* The screen. The old drawing left it out entirely, which is why the
     * middle read as a gap with the labels floating in it. */
    bk_fill(cr, "#7E8780", 60, 90, 90, 46, 10);
    bk_fill(cr, "#C5CCC0", 62, 92, 86, 42, 9);
    bk_dot(cr, "#3F4637", 105, 106, 3.1);            /* the running figure */
    bk_hex(cr, "#3F4637");
    cairo_set_line_width(cr, 2.6);
    cairo_set_line_cap(cr, CAIRO_LINE_CAP_ROUND);
    cairo_new_path(cr);
    cairo_move_to(cr, 105, 111); cairo_line_to(cr, 105, 120);
    cairo_move_to(cr, 105, 113); cairo_line_to(cr,  99, 117);
    cairo_move_to(cr, 105, 113); cairo_line_to(cr, 112, 115);
    cairo_move_to(cr, 105, 120); cairo_line_to(cr,  99, 126);
    cairo_move_to(cr, 105, 120); cairo_line_to(cr, 111, 125);
    cairo_stroke(cr);
    cairo_new_path(cr);

    /* a size smaller than the rest: at 11 it ran under the screen */
    bk_text(cr, "#1D1D1F", 22,  116, 10, TRUE, FALSE, "On-Off");
    bk_text(cr, "#1D1D1F", 160, 116, 11, TRUE, FALSE, "Run");
    bk_text(cr, "#1D1D1F", 72,  150, 14, TRUE, TRUE,  "A");
    bk_text(cr, "#1D1D1F", 105, 150, 14, TRUE, TRUE,  "B");
    bk_text(cr, "#1D1D1F", 138, 150, 14, TRUE, TRUE,  "C");

    bk_fill(cr, "#2B2B2D", 22,  90,  30, 15, 3);     /* View  */
    bk_fill(cr, "#2B2B2D", 158, 90,  30, 15, 3);     /* Prgm  */
    bk_fill(cr, "#D4302B", 22,  120, 30, 16, 3);     /* On-Off */
    bk_fill(cr, "#189A48", 158, 120, 30, 16, 3);     /* Run   */

    /* Outputs: three ports again, and the same height as the inputs. The
     * old one was nearly twice as tall; on the brick they match, and the
     * plain yellow that leaves below is on the real one too. */
    bk_fill(cr, "#4A4A4C", 30, 156, 150, 46, 7);     /* outputs A B C */
    for (int port = 0; port < 3; port++)
        for (int row = 0; row < 2; row++)
            for (int col = 0; col < 2; col++)
                bk_fill(cr, "#161618", 34 + port * 54 + col * 18,
                        162 + row * 19, 16, 15, 2.5);

    bk_text(cr, "#1D1D1F", 20, 252, 12, TRUE, FALSE, "RCX 2.0");
    cairo_save(cr);
    cairo_translate(cr, 190, 214);
    cairo_rotate(cr, G_PI / 2);
    bk_text(cr, "#1D1D1F", 0, 0, 11, TRUE, FALSE, "123456");
    cairo_restore(cr);

    cairo_restore(cr);
}

/* ---------------------------------------------------------------- Scout */
static void bk_draw_scout(cairo_t *cr, int w, int h) {
    cairo_save(cr);
    bk_begin(cr, w, h, 214, 290);

    bk_fill(cr, "#123A7A", 6, 10, 202, 276, 14);
    bk_fill(cr, "#1B50AE", 6, 6,  202, 276, 14);

    bk_fill(cr, "#17181A", 88, 0, 38, 34, 9);        /* light sensor barrel */
    bk_dot(cr, "#0E0F10", 107, 30, 13);
    bk_dot(cr, "#F2C81B", 34, 26, 6);                /* the little sun */
    bk_dot(cr, "#17181A", 52, 36, 4.5);
    bk_dot(cr, "#17181A", 68, 36, 4.5);
    bk_dot(cr, "#17181A", 146, 36, 4.5);
    bk_dot(cr, "#17181A", 162, 36, 4.5);

    /* the yellow stud pads, ports 1 and 2 */
    bk_fill(cr, "#E8C219", 26, 48, 56, 38, 5);
    bk_dot(cr, "#C9A510", 40, 60, 6);  bk_dot(cr, "#C9A510", 68, 60, 6);
    bk_dot(cr, "#C9A510", 40, 76, 6);  bk_dot(cr, "#C9A510", 68, 76, 6);
    bk_fill(cr, "#E8C219", 132, 48, 56, 38, 5);
    bk_dot(cr, "#C9A510", 146, 60, 6); bk_dot(cr, "#C9A510", 174, 60, 6);
    bk_dot(cr, "#C9A510", 146, 76, 6); bk_dot(cr, "#C9A510", 174, 76, 6);

    bk_text(cr, "#FFFFFF", 14,  70, 13, TRUE, FALSE, "1");
    bk_text(cr, "#FFFFFF", 194, 70, 13, TRUE, FALSE, "2");
    bk_text(cr, "#FFFFFF", 56,  99, 10, TRUE, FALSE, "Motion");
    bk_text(cr, "#FFFFFF", 98,  99, 10, TRUE, FALSE, "Touch");
    bk_text(cr, "#FFFFFF", 140, 99, 10, TRUE, FALSE, "Light");
    bk_text(cr, "#FFFFFF", 16,  116, 10, TRUE, FALSE, "Select");
    bk_text(cr, "#FFFFFF", 158, 116, 10, TRUE, FALSE, "Change");
    bk_text(cr, "#FFFFFF", 16,  152, 10, TRUE, FALSE, "On-Off");
    bk_text(cr, "#FFFFFF", 168, 152, 10, TRUE, FALSE, "Run");
    bk_text(cr, "#FFFFFF", 22,  196, 10, TRUE, FALSE, "Time");
    bk_text(cr, "#FFFFFF", 166, 196, 10, TRUE, FALSE, "FX");
    bk_text(cr, "#FFFFFF", 107, 198, 13, TRUE, TRUE,  "SCOUT");

    bk_fill(cr, "#232528", 16,  120, 34, 14, 3);
    bk_fill(cr, "#232528", 164, 120, 34, 14, 3);
    bk_fill(cr, "#D4302B", 16,  156, 34, 15, 3);
    bk_fill(cr, "#189A48", 164, 156, 34, 15, 3);

    bk_fill(cr, "#1E2023", 58, 104, 98, 78, 4);      /* the menu LCD */
    bk_fill(cr, "#A9C19B", 62, 108, 90, 70, 2);
    bk_text(cr, "#3E4C39", 65,  119, 6.5, FALSE, FALSE, "Forward");
    bk_text(cr, "#3E4C39", 92,  119, 6.5, FALSE, FALSE, "Reverse");
    bk_text(cr, "#3E4C39", 120, 119, 6.5, FALSE, FALSE, "Seek");
    bk_text(cr, "#3E4C39", 120, 130, 6.5, FALSE, FALSE, "Avoid");
    bk_text(cr, "#3E4C39", 120, 141, 6.5, FALSE, FALSE, "WaitFor");
    bk_text(cr, "#3E4C39", 120, 152, 6.5, FALSE, FALSE, "Brake");
    bk_hex(cr, "#3E4C39");
    cairo_set_line_width(cr, 1.4);
    cairo_new_path(cr);
    cairo_arc(cr, 72, 166, 4, 0, 2 * G_PI); cairo_stroke(cr);
    cairo_new_path(cr);
    cairo_arc(cr, 84, 166, 4, 0, 2 * G_PI); cairo_stroke(cr);

    /* output pads A and B */
    bk_fill(cr, "#17181A", 24, 206, 62, 54, 6);
    bk_dot(cr, "#3A3C40", 40, 222, 9);  bk_dot(cr, "#3A3C40", 70, 222, 9);
    bk_dot(cr, "#3A3C40", 40, 245, 9);  bk_dot(cr, "#3A3C40", 70, 245, 9);
    bk_fill(cr, "#17181A", 128, 206, 62, 54, 6);
    bk_dot(cr, "#3A3C40", 144, 222, 9); bk_dot(cr, "#3A3C40", 174, 222, 9);
    bk_dot(cr, "#3A3C40", 144, 245, 9); bk_dot(cr, "#3A3C40", 174, 245, 9);
    bk_text(cr, "#FFFFFF", 14,  214, 11, TRUE, FALSE, "A");
    bk_text(cr, "#FFFFFF", 196, 214, 11, TRUE, FALSE, "B");

    bk_hex(cr, "#9BA1A8");                           /* the arrow keys */
    const double up[2] = { 98, 118 };
    for (int i = 0; i < 2; i++) {
        cairo_move_to(cr, up[i], 214);
        cairo_line_to(cr, up[i] + 9, 225);
        cairo_line_to(cr, up[i] - 9, 225);
        cairo_close_path(cr); cairo_fill(cr);
        cairo_move_to(cr, up[i], 252);
        cairo_line_to(cr, up[i] - 9, 241);
        cairo_line_to(cr, up[i] + 9, 241);
        cairo_close_path(cr); cairo_fill(cr);
    }
    bk_dot(cr, "#123A7A", 107, 272, 9);

    cairo_restore(cr);
}

/* ------------------------------------------------------------------ NXT */
static void bk_draw_nxt(cairo_t *cr, int w, int h) {
    cairo_save(cr);
    bk_begin(cr, w, h, 206, 268);

    bk_fill(cr, "#86888C", 20, 0, 166, 26, 5);       /* A B C and USB */
    bk_text(cr, "#2E3034", 42,  16, 9, TRUE, FALSE, "A");
    bk_text(cr, "#2E3034", 78,  16, 9, TRUE, FALSE, "B");
    bk_text(cr, "#2E3034", 114, 16, 9, TRUE, FALSE, "C");
    bk_fill(cr, "#B9BBBF", 140, 4, 38, 18, 3);
    bk_text(cr, "#2E3034", 147, 17, 8, TRUE, FALSE, "USB");

    bk_fill(cr, "#BEC1C6", 12, 22, 182, 222, 16);
    bk_fill(cr, "#EFF1F3", 12, 18, 182, 222, 16);
    bk_fill(cr, "#DCDEE2", 4,   62, 14, 52, 6);      /* the side ridges */
    bk_fill(cr, "#DCDEE2", 188, 62, 14, 52, 6);

    bk_fill(cr, "#9DA0A5", 42, 36, 122, 92, 5);      /* the screen */
    bk_fill(cr, "#A8BE9C", 47, 41, 112, 82, 3);

    for (int i = 0; i < 4; i++)                      /* speaker grille */
        bk_fill(cr, "#6E7278", 168, 112 + i * 8, 18, 3.4, 1.7);

    bk_fill(cr, "#C9CBCF", 101, 130, 4, 18, 0);
    bk_fill(cr, "#EF8019", 86, 146, 34, 34, 5);      /* enter */
    bk_hex(cr, "#C3C6CB");                           /* the arrows, outward */
    cairo_move_to(cr, 46, 163); cairo_line_to(cr, 74, 150);
    cairo_line_to(cr, 74, 176); cairo_close_path(cr); cairo_fill(cr);
    cairo_move_to(cr, 160, 163); cairo_line_to(cr, 132, 150);
    cairo_line_to(cr, 132, 176); cairo_close_path(cr); cairo_fill(cr);
    bk_fill(cr, "#8E9196", 88, 188, 30, 17, 5);      /* back */

    bk_text(cr, "#5E6166", 103, 232, 23, TRUE, TRUE, "nxt");

    bk_fill(cr, "#86888C", 20, 240, 166, 26, 5);     /* 1 2 3 4 */
    bk_text(cr, "#2E3034", 40,  257, 9, TRUE, FALSE, "1");
    bk_text(cr, "#2E3034", 76,  257, 9, TRUE, FALSE, "2");
    bk_text(cr, "#2E3034", 112, 257, 9, TRUE, FALSE, "3");
    bk_text(cr, "#2E3034", 148, 257, 9, TRUE, FALSE, "4");

    cairo_restore(cr);
}

/* ------------------------------------------------------------------ EV3 */

/* A rounded rectangle filled top to bottom, for the bezel and the foot. */
static void bk_vgrad(cairo_t *cr, const char *top, const char *bottom,
                     double x, double y, double w, double h, double r) {
    unsigned int a[3] = {0, 0, 0}, b[3] = {0, 0, 0};
    sscanf(top + 1, "%02x%02x%02x", &a[0], &a[1], &a[2]);
    sscanf(bottom + 1, "%02x%02x%02x", &b[0], &b[1], &b[2]);
    cairo_pattern_t *p = cairo_pattern_create_linear(0, y, 0, y + h);
    cairo_pattern_add_color_stop_rgb(p, 0, a[0] / 255.0, a[1] / 255.0, a[2] / 255.0);
    cairo_pattern_add_color_stop_rgb(p, 1, b[0] / 255.0, b[1] / 255.0, b[2] / 255.0);
    cairo_set_source(cr, p);
    bk_rrect(cr, x, y, w, h, r);
    cairo_fill(cr);
    cairo_pattern_destroy(p);
}

/* A closed polygon from x,y pairs. */
static void bk_poly(cairo_t *cr, const char *hex, const double *pt, int n) {
    bk_hex(cr, hex);
    cairo_new_path(cr);
    cairo_move_to(cr, pt[0], pt[1]);
    for (int i = 1; i < n; i++) cairo_line_to(cr, pt[i * 2], pt[i * 2 + 1]);
    cairo_close_path(cr);
    cairo_fill(cr);
}

/* The red the buttons glow with: bright in the middle, gone at the edge. */
static void bk_glow(cairo_t *cr, double cx, double cy, double r) {
    cairo_pattern_t *p = cairo_pattern_create_radial(cx, cy, 0, cx, cy, r);
    cairo_pattern_add_color_stop_rgba(p, 0.00, 1.00, 0.945, 0.933, 1.0);
    cairo_pattern_add_color_stop_rgba(p, 0.25, 1.00, 0.294, 0.243, 0.95);
    cairo_pattern_add_color_stop_rgba(p, 1.00, 0.898, 0.188, 0.169, 0.0);
    cairo_set_source(cr, p);
    cairo_new_path(cr);
    cairo_arc(cr, cx, cy, r, 0, 2 * G_PI);
    cairo_fill(cr);
    cairo_pattern_destroy(p);
}

static void bk_draw_ev3(cairo_t *cr, int w, int h) {
    cairo_save(cr);
    bk_begin(cr, w, h, 176, 254);

    /* the ridges either side, behind the body */
    bk_fill(cr, "#E4E5E7", 6,   49, 14, 159, 3);
    bk_fill(cr, "#E4E5E7", 156, 49, 14, 159, 3);

    bk_fill(cr, "#B9BABD", 15, 3, 142, 251, 9);      /* the edge below */

    /* the body: white, a grey bezel over the screen, a darker foot */
    cairo_save(cr);
    bk_rrect(cr, 15, 0, 142, 252, 9);
    cairo_clip(cr);
    bk_vgrad(cr, "#F7F7F8", "#ECECEE", 15, 0,   142, 252, 0);
    bk_vgrad(cr, "#E2E3E5", "#C9CACD", 15, 0,   142, 118, 0);
    bk_fill(cr, "#C3C4C7", 15, 112, 142, 6, 0);
    bk_vgrad(cr, "#B2B3B6", "#9FA0A4", 15, 218, 142, 34, 0);
    bk_fill(cr, "#A5A6A9", 15, 218, 142, 1.6, 0);
    cairo_restore(cr);

    /* the screen: a black window with a grey LCD in it */
    bk_fill(cr, "#1A1A1B", 28, 22, 116, 70, 6);
    bk_fill(cr, "#3E4041", 37, 26, 98, 62, 1.5);
    bk_fill(cr, "#575A5B", 38, 27, 96, 60, 1);
    bk_text(cr, "#1C1E1E", 86, 31.6, 5.6, TRUE, TRUE, "EV3");
    cairo_new_path(cr);
    bk_hex(cr, "#1C1E1E");                           /* battery and rules */
    cairo_set_line_width(cr, 0.7);
    bk_rrect(cr, 120, 28.2, 12, 4.4, 1);
    cairo_stroke(cr);
    cairo_new_path(cr);
    cairo_rectangle(cr, 121.2, 29.3, 8.4, 2.2);
    cairo_fill(cr);
    cairo_move_to(cr, 38, 34);   cairo_line_to(cr, 134, 34);
    cairo_move_to(cr, 38, 46);   cairo_line_to(cr, 121, 46);
    cairo_stroke(cr);
    cairo_new_path(cr);
    bk_rrect(cr, 123, 47.5, 6, 38, 1);               /* scroll bar */
    cairo_stroke(cr);
    cairo_new_path(cr);
    cairo_rectangle(cr, 124, 48.6, 4, 3.4);
    cairo_fill(cr);

    /* the four tabs: run, files, apps, settings */
    cairo_set_line_width(cr, 0.9);
    cairo_set_line_join(cr, CAIRO_LINE_JOIN_ROUND);
    cairo_set_line_cap(cr, CAIRO_LINE_CAP_ROUND);
    cairo_new_path(cr);                              /* the open one, run */
    cairo_move_to(cr, 44, 45.5);  cairo_line_to(cr, 44, 39);
    cairo_arc(cr, 46, 39, 2, G_PI, 3 * G_PI / 2);
    cairo_line_to(cr, 59, 37);
    cairo_arc(cr, 59, 39, 2, -G_PI / 2, 0);
    cairo_line_to(cr, 61, 45.5);
    cairo_stroke(cr);
    for (int i = 0; i < 3; i++) {
        cairo_new_path(cr);
        bk_rrect(cr, 66 + i * 20, 37, 15, 8.5, 2);
        cairo_stroke(cr);
    }
    cairo_new_path(cr);
    cairo_arc(cr, 52.5, 41.4, 3, 0, 2 * G_PI);       /* run: circle + triangle */
    cairo_stroke(cr);
    cairo_new_path(cr);
    cairo_move_to(cr, 51.6, 39.9); cairo_line_to(cr, 54.4, 41.4);
    cairo_line_to(cr, 51.6, 42.9); cairo_close_path(cr);
    cairo_fill(cr);
    cairo_new_path(cr);                              /* files: a page */
    cairo_move_to(cr, 71, 39);     cairo_line_to(cr, 75.2, 39);
    cairo_line_to(cr, 77, 40.8);   cairo_line_to(cr, 77, 44);
    cairo_line_to(cr, 71, 44);     cairo_close_path(cr);
    cairo_stroke(cr);
    cairo_new_path(cr);                              /* apps: a grid */
    for (int r = 0; r < 2; r++)
        for (int c = 0; c < 3; c++) {
            cairo_move_to(cr, 91 + c * 3,     39.4 + r * 3.5);
            cairo_line_to(cr, 92.6 + c * 3,   39.4 + r * 3.5);
        }
    cairo_stroke(cr);
    cairo_new_path(cr);                              /* settings: a wrench */
    cairo_move_to(cr, 109.6, 43.6); cairo_line_to(cr, 116, 38.4);
    cairo_stroke(cr);
    cairo_new_path(cr);
    cairo_arc(cr, 117.2, 38.2, 1.5, 0, 2 * G_PI);
    cairo_stroke(cr);
    cairo_new_path(cr);

    /* the little grey tab, with a corner cut off it */
    {
        const double tab[] = { 24, 122,  58, 122,  58, 133,  54, 137,  24, 137 };
        bk_poly(cr, "#C7C8CB", tab, 5);
    }

    /* the buttons: an octagon of up and down, a pill either side, a square
     * in the middle */
    {
        const double out[] = { 71,130, 77,128, 95,128, 101,130, 109,138,
                               109,190, 101,198, 95,200, 77,200, 71,198,
                               63,190, 63,138 };
        const double in[]  = { 72,132, 78,130, 94,130, 100,132, 107,139,
                               107,189, 100,196, 94,198, 78,198, 72,196,
                               65,189, 65,139 };
        bk_poly(cr, "#3A3A3D", out, 12);
        bk_poly(cr, "#C5C6C9", in, 12);
    }
    bk_fill(cr, "#3A3A3D", 39,  152, 37, 24, 12);
    bk_fill(cr, "#C5C6C9", 41,  154, 33, 20, 10);
    bk_fill(cr, "#3A3A3D", 104, 152, 31, 24, 12);
    bk_fill(cr, "#C5C6C9", 106, 154, 27, 20, 10);
    bk_fill(cr, "#3A3A3D", 76,  152.5, 24, 24, 5);
    bk_fill(cr, "#E9EAEC", 78,  154.5, 20, 20, 3.4);
    bk_fill(cr, "#B7B8BB", 79.4, 155.9, 17.2, 17.2, 2);

    /* lit red from underneath, in the gaps either side of the middle */
    bk_glow(cr, 66.5, 163.5, 9);
    bk_glow(cr, 105.5, 163.5, 9);
    bk_hex(cr, "#FF5A4D");
    cairo_set_line_width(cr, 1.1);
    cairo_set_line_cap(cr, CAIRO_LINE_CAP_ROUND);
    cairo_new_path(cr);
    cairo_move_to(cr, 63, 163.5);  cairo_line_to(cr, 77, 163.5);
    cairo_move_to(cr, 99, 163.5);  cairo_line_to(cr, 113, 163.5);
    cairo_stroke(cr);
    cairo_new_path(cr);

    /* the name, pressed into the foot: a shade under, a highlight over */
    bk_text(cr, "#8F9094", 23, 236.5, 14.5, TRUE, FALSE, "EV3");
    cairo_new_path(cr);
    bk_text(cr, "#E1E2E4", 23, 235.4, 14.5, TRUE, FALSE, "EV3");
    cairo_new_path(cr);

    cairo_restore(cr);
}
