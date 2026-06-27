<?php get_header(); ?>

<div class="catalog-header">
    <h1>
        <?php
        if (is_tax('kategorie_potravin')) {
            echo esc_html(single_term_title('', false));
        } else {
            echo 'Potraviny';
        }
        ?>
    </h1>
    <a href="<?php echo esc_url(home_url('/')); ?>" class="back-link">&larr; Zpět na katalog</a>
</div>

<div class="catalog-grid">
    <?php if (have_posts()):
        while (have_posts()): the_post();
            $kcal    = get_post_meta(get_the_ID(), '_jidlo_energie_kcal', true);
            $protein = get_post_meta(get_the_ID(), '_jidlo_bilkoviny', true);
            $carbs   = get_post_meta(get_the_ID(), '_jidlo_sacharidy', true);
            $fat     = get_post_meta(get_the_ID(), '_jidlo_tuky', true);
            $brand   = get_post_meta(get_the_ID(), '_jidlo_znacka', true);
    ?>
        <div class="food-card">
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
        the_posts_pagination();
    else: ?>
        <div class="catalog-empty">
            <p>Žádné potraviny v této kategorii.</p>
        </div>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
