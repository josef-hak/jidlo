<?php get_header(); ?>

<?php while (have_posts()): the_post(); ?>

<a href="<?php echo esc_url(home_url('/')); ?>" class="back-link">&larr; Zpět na katalog</a>

<div class="food-detail">
    <?php if (has_post_thumbnail()): ?>
        <div class="food-detail-image">
            <?php the_post_thumbnail('food-full'); ?>
        </div>
    <?php endif; ?>

    <div class="food-detail-body">
        <h1 class="food-detail-title"><?php the_title(); ?></h1>

        <?php $brand = get_post_meta(get_the_ID(), '_jidlo_znacka', true); ?>
        <?php if ($brand): ?>
            <div class="food-detail-brand"><?php echo esc_html($brand); ?></div>
        <?php endif; ?>

        <?php $popis = get_post_meta(get_the_ID(), '_jidlo_popis', true); ?>
        <?php if ($popis): ?>
            <p class="food-detail-description"><?php echo esc_html($popis); ?></p>
        <?php endif; ?>

        <?php
        $terms = get_the_terms(get_the_ID(), 'kategorie_potravin');
        if (!empty($terms) && !is_wp_error($terms)):
            foreach ($terms as $term): ?>
                <span class="food-detail-category"><?php echo esc_html($term->name); ?></span>
            <?php endforeach;
        endif;
        ?>

        <table class="nutrition-table">
            <caption>Nutriční hodnoty na 100 g</caption>
            <tbody>
                <?php
                $fields = JIDLO_NUTRI_FIELDS;
                $sub_keys = ['nasycene_mk', 'cukry'];

                foreach ($fields as $key => $field):
                    $value = get_post_meta(get_the_ID(), '_jidlo_' . $key, true);
                    $is_sub = in_array($key, $sub_keys);
                ?>
                <tr<?php echo $is_sub ? ' class="sub"' : ''; ?>>
                    <th><?php echo esc_html($field['label']); ?></th>
                    <td><?php echo $value !== '' ? esc_html($value) . ' ' . esc_html($field['unit']) : '—'; ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>

        <?php if (get_the_content()): ?>
            <div class="food-detail-notes">
                <h3>Poznámky</h3>
                <?php the_content(); ?>
            </div>
        <?php endif; ?>

        <?php if (is_user_logged_in()): ?>
            <div class="food-detail-actions">
                <a href="<?php echo esc_url(get_edit_post_link()); ?>" class="btn btn-secondary">Upravit</a>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php endwhile; ?>

<?php get_footer(); ?>
