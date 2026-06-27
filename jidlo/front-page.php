<?php get_header(); ?>

<div class="catalog-header">
    <h1>Katalog potravin</h1>
    <input type="search" class="catalog-search" id="food-search" placeholder="Hledat potravinu...">

    <?php
    $categories = get_terms([
        'taxonomy'   => 'kategorie_potravin',
        'hide_empty' => false,
    ]);
    if (!empty($categories) && !is_wp_error($categories)): ?>
        <div class="catalog-filters">
            <button class="filter-pill active" data-category="">Vše</button>
            <?php foreach ($categories as $cat): ?>
                <button class="filter-pill" data-category="<?php echo esc_attr($cat->slug); ?>">
                    <?php echo esc_html($cat->name); ?>
                </button>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</div>

<div class="catalog-grid">
    <?php
    $foods = new WP_Query([
        'post_type'      => 'potravina',
        'posts_per_page' => -1,
        'orderby'        => 'date',
        'order'          => 'DESC',
    ]);

    if ($foods->have_posts()):
        while ($foods->have_posts()): $foods->the_post();
            $kcal     = get_post_meta(get_the_ID(), '_jidlo_energie_kcal', true);
            $protein  = get_post_meta(get_the_ID(), '_jidlo_bilkoviny', true);
            $carbs    = get_post_meta(get_the_ID(), '_jidlo_sacharidy', true);
            $fat      = get_post_meta(get_the_ID(), '_jidlo_tuky', true);
            $brand    = get_post_meta(get_the_ID(), '_jidlo_znacka', true);
            $terms    = get_the_terms(get_the_ID(), 'kategorie_potravin');
            $cat_slug = (!empty($terms) && !is_wp_error($terms)) ? $terms[0]->slug : '';
    ?>
        <div class="food-card" data-category="<?php echo esc_attr($cat_slug); ?>">
            <a href="<?php the_permalink(); ?>">
                <div class="food-card-image">
                    <?php if (has_post_thumbnail()): ?>
                        <?php the_post_thumbnail('food-thumb'); ?>
                    <?php endif; ?>
                </div>
                <div class="food-card-body">
                    <div class="food-card-title"><?php the_title(); ?></div>
                    <?php if ($brand): ?>
                        <div class="food-card-brand"><?php echo esc_html($brand); ?></div>
                    <?php endif; ?>
                    <div class="food-card-macros">
                        <div><span class="macro-value"><?php echo $kcal !== '' ? esc_html($kcal) : '—'; ?></span><span class="macro-label">kcal</span></div>
                        <div><span class="macro-value"><?php echo $protein !== '' ? esc_html($protein) : '—'; ?></span><span class="macro-label">bílk.</span></div>
                        <div><span class="macro-value"><?php echo $carbs !== '' ? esc_html($carbs) : '—'; ?></span><span class="macro-label">sach.</span></div>
                        <div><span class="macro-value"><?php echo $fat !== '' ? esc_html($fat) : '—'; ?></span><span class="macro-label">tuky</span></div>
                    </div>
                </div>
            </a>
        </div>
    <?php
        endwhile;
        wp_reset_postdata();
    else:
    ?>
        <div class="catalog-empty">
            <p>Zatím žádné potraviny.</p>
            <?php if (is_user_logged_in()): ?>
                <p><a href="<?php echo esc_url(home_url('/pridat/')); ?>">Přidat první potravinu &rarr;</a></p>
            <?php endif; ?>
        </div>
    <?php endif; ?>
</div>

<?php if (is_user_logged_in()): ?>
    <a href="<?php echo esc_url(home_url('/pridat/')); ?>" class="fab" title="Přidat potravinu">+</a>
<?php endif; ?>

<?php get_footer(); ?>
