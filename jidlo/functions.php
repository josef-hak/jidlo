<?php

define('JIDLO_VERSION', '1.0.0');

require get_template_directory() . '/inc/cpt-potravina.php';
require get_template_directory() . '/inc/meta-boxes.php';
require get_template_directory() . '/inc/ajax-handlers.php';

function jidlo_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['search-form', 'gallery', 'caption', 'style', 'script']);

    add_image_size('food-thumb', 400, 400, true);
    add_image_size('food-full', 800, 800, false);

    register_nav_menus([
        'primary' => 'Hlavní menu',
    ]);
}
add_action('after_setup_theme', 'jidlo_setup');

function jidlo_scripts() {
    wp_enqueue_style('jidlo-style', get_stylesheet_uri(), [], JIDLO_VERSION);

    if (is_front_page() || is_post_type_archive('potravina') || is_tax('kategorie_potravin')) {
        wp_enqueue_script('jidlo-catalog', get_template_directory_uri() . '/assets/js/catalog.js', [], JIDLO_VERSION, true);
    }

    if (is_page_template('page-templates/template-pridat.php')) {
        wp_enqueue_script('jidlo-food-form', get_template_directory_uri() . '/assets/js/food-form.js', [], JIDLO_VERSION, true);
        wp_localize_script('jidlo-food-form', 'jidloAjax', [
            'url'   => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('jidlo_food_nonce'),
        ]);
    }
}
add_action('wp_enqueue_scripts', 'jidlo_scripts');

function jidlo_activate() {
    // Create "Přidat potravinu" page
    if (!get_page_by_path('pridat')) {
        wp_insert_post([
            'post_type'    => 'page',
            'post_title'   => 'Přidat potravinu',
            'post_name'    => 'pridat',
            'post_status'  => 'publish',
            'post_content' => '',
            'page_template' => 'page-templates/template-pridat.php',
        ]);
    }

    // Create default food categories
    jidlo_create_default_categories();

    // Flush rewrite rules
    jidlo_register_cpt();
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'jidlo_activate');

/**
 * Get category SVG icon URL for a food item.
 * Falls back to "ostatni.svg" if category has no icon.
 */
function jidlo_category_icon_url($post_id = null) {
    $post_id = $post_id ?: get_the_ID();
    $terms = get_the_terms($post_id, 'kategorie_potravin');
    $slug = (!empty($terms) && !is_wp_error($terms)) ? $terms[0]->slug : 'ostatni';

    $icon_path = get_template_directory() . '/assets/imgs/' . $slug . '.svg';
    if (file_exists($icon_path)) {
        return get_template_directory_uri() . '/assets/imgs/' . $slug . '.svg';
    }
    return get_template_directory_uri() . '/assets/imgs/ostatni.svg';
}
