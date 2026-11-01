/* The three bricks, drawn with Cairo.
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
#define BK_SCALE 0.85

/* Fit a design-space box of dw x dh into the widget, centred. */
static void bk_begin(cairo_t *cr, int w, int h, double dw, double dh) {
    double s = MIN(w / dw, h / dh) * BK_SCALE;
    cairo_translate(cr, (w - dw * s) / 2, (h - dh * s) / 2);
    cairo_scale(cr, s, s);
}

/* ------------------------------------------------------------------ RCX */
static void bk_draw_rcx(cairo_t *cr, int w, int h) {
    cairo_save(cr);
    bk_begin(cr, w, h, 210, 272);

    bk_fill(cr, "#C9A510", 6, 6, 198, 260, 13);      /* the edge below */
    bk_fill(cr, "#F4C81B", 6, 2, 198, 260, 13);      /* the yellow face */
    bk_fill(cr, "#1D1D1F", 74, 2, 62, 17, 4);        /* dark block on top */

    bk_fill(cr, "#9A9A9A", 30, 26, 150, 46, 7);      /* input pads 1 2 3 */
    for (int row = 0; row < 2; row++)
        for (int col = 0; col < 4; col++)
            bk_fill(cr, "#C2C2C2", 38 + col * 32, 33 + row * 18, 26, 14, 2.5);

    bk_text(cr, "#1D1D1F", 27,  88, 11, TRUE, FALSE, "View");
    bk_text(cr, "#1D1D1F", 155, 88, 11, TRUE, FALSE, "Prgm");
    bk_text(cr, "#1D1D1F", 72,  95, 15, TRUE, FALSE, "1");
    bk_text(cr, "#1D1D1F", 99,  95, 15, TRUE, FALSE, "2");
    bk_text(cr, "#1D1D1F", 126, 95, 15, TRUE, FALSE, "3");
    bk_text(cr, "#1D1D1F", 22,  118, 11, TRUE, FALSE, "On-Off");
    bk_text(cr, "#1D1D1F", 160, 118, 11, TRUE, FALSE, "Run");
    bk_text(cr, "#1D1D1F", 72,  126, 15, TRUE, FALSE, "A");
    bk_text(cr, "#1D1D1F", 98,  126, 15, TRUE, FALSE, "B");
    bk_text(cr, "#1D1D1F", 124, 126, 15, TRUE, FALSE, "C");

    bk_fill(cr, "#2B2B2D", 22,  92,  30, 15, 3);     /* View  */
    bk_fill(cr, "#2B2B2D", 158, 92,  30, 15, 3);     /* Prgm  */
    bk_fill(cr, "#D4302B", 22,  122, 30, 16, 3);     /* On-Off */
    bk_fill(cr, "#189A48", 158, 122, 30, 16, 3);     /* Run   */

    bk_fill(cr, "#4A4A4C", 30, 146, 150, 78, 7);     /* output pads A B C */
    for (int row = 0; row < 4; row++)
        for (int col = 0; col < 4; col++)
            bk_fill(cr, "#161618", 38 + col * 32, 154 + row * 18,
                    26, row == 3 ? 10 : 14, 2.5);

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
