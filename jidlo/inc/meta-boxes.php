<?php

define('JIDLO_NUTRI_FIELDS', [
    'energie_kj'  => ['label' => 'Energetická hodnota (kJ)',         'unit' => 'kJ'],
    'energie_kcal' => ['label' => 'Energetická hodnota (kcal)',       'unit' => 'kcal'],
    'bilkoviny'    => ['label' => 'Bílkoviny',                         'unit' => 'g'],
    'sacharidy'    => ['label' => 'Sacharidy',                         'unit' => 'g'],
    'cukry'        => ['label' => '— z toho cukry',                    'unit' => 'g'],
    'vlaknina'     => ['label' => 'Vláknina',                          'unit' => 'g'],
    'tuky'         => ['label' => 'Tuky',                              'unit' => 'g'],
    'nasycene_mk'  => ['label' => '— z toho nasycené mastné kyseliny', 'unit' => 'g'],
    'sul'          => ['label' => 'Sůl',                               'unit' => 'g'],
]);

function jidlo_add_meta_boxes() {
    add_meta_box(
        'jidlo_nutri',
        'Nutriční hodnoty (na 100 g)',
        'jidlo_nutri_meta_box_html',
        'potravina',
        'normal',
        'high'
    );

    add_meta_box(
        'jidlo_popis',
        'Popis',
        'jidlo_popis_meta_box_html',
        'potravina',
        'normal',
        'high'
    );

    add_meta_box(
        'jidlo_znacka',
        'Značka / Výrobce',
        'jidlo_znacka_meta_box_html',
        'potravina',
        'side',
        'default'
    );
}
add_action('add_meta_boxes_potravina', 'jidlo_add_meta_boxes');

function jidlo_nutri_meta_box_html($post) {
    wp_nonce_field('jidlo_nutri_save', 'jidlo_nutri_nonce');
    echo '<table class="form-table"><tbody>';

    foreach (JIDLO_NUTRI_FIELDS as $key => $field) {
        $value = get_post_meta($post->ID, '_jidlo_' . $key, true);
        $indent = str_starts_with($field['label'], '—') ? ' style="padding-left:20px;color:#666"' : '';
        echo '<tr>';
        echo '<th' . $indent . '><label for="jidlo_' . $key . '">' . esc_html($field['label']) . '</label></th>';
        echo '<td><input type="number" step="0.01" min="0" id="jidlo_' . $key . '" name="jidlo_' . $key . '" value="' . esc_attr($value) . '" style="width:100px"> ' . esc_html($field['unit']) . '</td>';
        echo '</tr>';
    }

    echo '</tbody></table>';
}

function jidlo_popis_meta_box_html($post) {
    $value = get_post_meta($post->ID, '_jidlo_popis', true);
    echo '<textarea name="jidlo_popis" rows="2" maxlength="300" class="widefat" placeholder="Krátký popis potraviny (do 300 znaků)">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">' . mb_strlen($value) . ' / 300 znaků</p>';
}

function jidlo_znacka_meta_box_html($post) {
    $value = get_post_meta($post->ID, '_jidlo_znacka', true);
    echo '<input type="text" name="jidlo_znacka" value="' . esc_attr($value) . '" class="widefat">';
}

function jidlo_save_meta($post_id) {
    if (!isset($_POST['jidlo_nutri_nonce']) || !wp_verify_nonce($_POST['jidlo_nutri_nonce'], 'jidlo_nutri_save')) {
        return;
    }

    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
        return;
    }

    if (!current_user_can('edit_post', $post_id)) {
        return;
    }

    foreach (JIDLO_NUTRI_FIELDS as $key => $field) {
        if (isset($_POST['jidlo_' . $key]) && $_POST['jidlo_' . $key] !== '') {
            update_post_meta($post_id, '_jidlo_' . $key, floatval($_POST['jidlo_' . $key]));
        } else {
            delete_post_meta($post_id, '_jidlo_' . $key);
        }
    }

    if (isset($_POST['jidlo_popis'])) {
        update_post_meta($post_id, '_jidlo_popis', sanitize_textarea_field(mb_substr($_POST['jidlo_popis'], 0, 300)));
    }

    if (isset($_POST['jidlo_znacka'])) {
        update_post_meta($post_id, '_jidlo_znacka', sanitize_text_field($_POST['jidlo_znacka']));
    }
}
add_action('save_post_potravina', 'jidlo_save_meta');
