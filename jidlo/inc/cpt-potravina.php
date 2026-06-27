<?php

function jidlo_register_cpt() {
    register_post_type('potravina', [
        'labels' => [
            'name'               => 'Potraviny',
            'singular_name'      => 'Potravina',
            'add_new'            => 'Přidat potravinu',
            'add_new_item'       => 'Přidat novou potravinu',
            'edit_item'          => 'Upravit potravinu',
            'new_item'           => 'Nová potravina',
            'view_item'          => 'Zobrazit potravinu',
            'search_items'       => 'Hledat potraviny',
            'not_found'          => 'Žádné potraviny nenalezeny',
            'not_found_in_trash' => 'Žádné potraviny v koši',
            'all_items'          => 'Všechny potraviny',
            'menu_name'          => 'Potraviny',
        ],
        'public'       => true,
        'has_archive'  => true,
        'menu_icon'    => 'dashicons-carrot',
        'supports'     => ['title', 'thumbnail', 'editor'],
        'rewrite'      => ['slug' => 'potravina'],
        'show_in_rest' => true,
    ]);

    register_taxonomy('kategorie_potravin', 'potravina', [
        'labels' => [
            'name'              => 'Kategorie potravin',
            'singular_name'     => 'Kategorie',
            'search_items'      => 'Hledat kategorie',
            'all_items'         => 'Všechny kategorie',
            'parent_item'       => 'Nadřazená kategorie',
            'parent_item_colon' => 'Nadřazená kategorie:',
            'edit_item'         => 'Upravit kategorii',
            'update_item'       => 'Aktualizovat kategorii',
            'add_new_item'      => 'Přidat kategorii',
            'new_item_name'     => 'Název nové kategorie',
            'menu_name'         => 'Kategorie',
        ],
        'hierarchical' => true,
        'show_in_rest' => true,
        'rewrite'      => ['slug' => 'kategorie'],
    ]);
}
add_action('init', 'jidlo_register_cpt');

function jidlo_create_default_categories() {
    $defaults = [
        'Mléčné výrobky',
        'Maso a uzeniny',
        'Ovoce',
        'Zelenina',
        'Pečivo a obiloviny',
        'Luštěniny a ořechy',
        'Nápoje',
        'Sladkosti',
        'Ostatní',
    ];

    foreach ($defaults as $name) {
        if (!term_exists($name, 'kategorie_potravin')) {
            wp_insert_term($name, 'kategorie_potravin');
        }
    }
}
