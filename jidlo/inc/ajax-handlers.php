<?php

function jidlo_handle_add_food() {
    check_ajax_referer('jidlo_food_nonce', 'nonce');

    if (!is_user_logged_in()) {
        wp_send_json_error(['message' => 'Musíte být přihlášeni.']);
    }

    $title = isset($_POST['food_title']) ? sanitize_text_field($_POST['food_title']) : '';
    if (empty($title)) {
        wp_send_json_error(['message' => 'Název potraviny je povinný.']);
    }

    $attachment_id = 0;
    if (!empty($_FILES['food_photo']) && $_FILES['food_photo']['error'] === UPLOAD_ERR_OK) {
        require_once ABSPATH . 'wp-admin/includes/image.php';
        require_once ABSPATH . 'wp-admin/includes/file.php';
        require_once ABSPATH . 'wp-admin/includes/media.php';

        $upload = wp_handle_upload($_FILES['food_photo'], ['test_form' => false]);

        if (isset($upload['error'])) {
            wp_send_json_error(['message' => 'Chyba nahrávání: ' . $upload['error']]);
        }

        $attachment_id = wp_insert_attachment([
            'post_mime_type' => $upload['type'],
            'post_title'     => sanitize_file_name($upload['file']),
            'post_content'   => '',
            'post_status'    => 'inherit',
        ], $upload['file']);

        $metadata = wp_generate_attachment_metadata($attachment_id, $upload['file']);
        wp_update_attachment_metadata($attachment_id, $metadata);
    }

    $post_id = wp_insert_post([
        'post_type'    => 'potravina',
        'post_status'  => 'publish',
        'post_title'   => $title,
        'post_content' => isset($_POST['food_notes']) ? sanitize_textarea_field($_POST['food_notes']) : '',
        'post_author'  => get_current_user_id(),
    ]);

    if (is_wp_error($post_id)) {
        wp_send_json_error(['message' => 'Chyba při ukládání.']);
    }

    if ($attachment_id) {
        set_post_thumbnail($post_id, $attachment_id);
    }

    if (!empty($_POST['food_category'])) {
        wp_set_object_terms($post_id, intval($_POST['food_category']), 'kategorie_potravin');
    }

    foreach (JIDLO_NUTRI_FIELDS as $key => $field) {
        if (isset($_POST['jidlo_' . $key]) && $_POST['jidlo_' . $key] !== '') {
            update_post_meta($post_id, '_jidlo_' . $key, floatval($_POST['jidlo_' . $key]));
        }
    }

    if (!empty($_POST['food_description'])) {
        update_post_meta($post_id, '_jidlo_popis', sanitize_textarea_field(mb_substr($_POST['food_description'], 0, 300)));
    }

    if (!empty($_POST['food_brand'])) {
        update_post_meta($post_id, '_jidlo_znacka', sanitize_text_field($_POST['food_brand']));
    }

    wp_send_json_success([
        'message' => 'Potravina uložena!',
        'url'     => get_permalink($post_id),
    ]);
}
add_action('wp_ajax_jidlo_add_food', 'jidlo_handle_add_food');
