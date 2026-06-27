<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
    <a href="<?php echo esc_url(home_url('/')); ?>" class="site-title"><?php bloginfo('name'); ?></a>
    <nav>
        <ul>
            <?php if (is_user_logged_in()): ?>
                <li><a href="<?php echo esc_url(home_url('/pridat/')); ?>">+ Přidat</a></li>
                <li><a href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>">Odhlásit</a></li>
            <?php else: ?>
                <li><a href="<?php echo esc_url(wp_login_url(home_url('/'))); ?>">Přihlásit</a></li>
            <?php endif; ?>
        </ul>
    </nav>
</header>

<main class="site-content">
