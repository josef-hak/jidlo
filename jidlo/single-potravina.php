<?php get_header(); ?>

<?php while (have_posts()): the_post(); ?>

<a href="<?php echo esc_url(home_url('/')); ?>" class="back-link">&larr; Zpět na katalog</a>

<div class="food-detail">
    <div class="food-detail-header">
        <div class="food-detail-icon-wrap">
            <?php if (has_post_thumbnail()): ?>
                <?php the_post_thumbnail('food-thumb'); ?>
            <?php else: ?>
                <img src="<?php echo esc_url(jidlo_category_icon_url()); ?>" alt="">
            <?php endif; ?>
        </div>
        <div class="food-detail-info">
            <h1 class="food-detail-title"><?php the_title(); ?></h1>

            <?php $brand = get_post_meta(get_the_ID(), '_jidlo_znacka', true); ?>
            <?php if ($brand): ?>
                <div class="food-detail-brand"><?php echo esc_html($brand); ?></div>
            <?php endif; ?>

            <?php
            $terms = get_the_terms(get_the_ID(), 'kategorie_potravin');
            if (!empty($terms) && !is_wp_error($terms)):
                foreach ($terms as $term): ?>
                    <span class="food-detail-category"><?php echo esc_html($term->name); ?></span>
                <?php endforeach;
            endif;
            ?>

            <?php $popis = get_post_meta(get_the_ID(), '_jidlo_popis', true); ?>
            <?php if ($popis): ?>
                <p class="food-detail-description"><?php echo esc_html($popis); ?></p>
            <?php endif; ?>
        </div>
    </div>

    <div class="food-detail-body">
        <?php
        $d_bilk = floatval(get_post_meta(get_the_ID(), '_jidlo_bilkoviny', true));
        $d_sach = floatval(get_post_meta(get_the_ID(), '_jidlo_sacharidy', true));
        $d_cukry = floatval(get_post_meta(get_the_ID(), '_jidlo_cukry', true));
        $d_tuky = floatval(get_post_meta(get_the_ID(), '_jidlo_tuky', true));
        $d_nmk = floatval(get_post_meta(get_the_ID(), '_jidlo_nasycene_mk', true));
        $d_total = $d_bilk + $d_sach + $d_tuky;
        $has_donut = $d_total > 0;

        if ($has_donut):
            $p_bilk = $d_bilk / $d_total * 100;
            $p_sach = $d_sach / $d_total * 100;
            $p_tuky = $d_tuky / $d_total * 100;
            $p_cukry = $d_sach > 0 ? ($d_cukry / $d_total * 100) : 0;
            $p_sach_rest = $p_sach - $p_cukry;
            $p_nmk = $d_tuky > 0 ? ($d_nmk / $d_total * 100) : 0;
            $p_tuky_rest = $p_tuky - $p_nmk;

            // Color map: key => [bg color for row, percentage]
            $color_map = [
                'bilkoviny'  => ['#e05555', $p_bilk],
                'tuky'       => ['#eebb44', $p_tuky],
                'nasycene_mk'=> ['#cc9922', $p_nmk],
                'sacharidy'  => ['#5588dd', $p_sach],
                'cukry'      => ['#2255aa', $p_cukry],
                'vlaknina'   => ['#aaccee', 0],
            ];
        endif;
        ?>

        <table class="nutrition-table">
            <caption>Nutriční hodnoty na 100 g</caption>
            <tbody>
                <?php
                $kj = get_post_meta(get_the_ID(), '_jidlo_energie_kj', true);
                $kcal = get_post_meta(get_the_ID(), '_jidlo_energie_kcal', true);
                ?>
                <tr>
                    <th>Energetická hodnota</th>
                    <td><?php
                        if ($kj !== '' || $kcal !== '') {
                            $parts = [];
                            if ($kj !== '') $parts[] = esc_html($kj) . ' kJ';
                            if ($kcal !== '') $parts[] = '(' . esc_html($kcal) . ' kcal)';
                            echo implode(' ', $parts);
                        } else {
                            echo '—';
                        }
                    ?></td>
                    <?php if ($has_donut): ?><td></td><?php endif; ?>
                </tr>
                <?php
                $fields = JIDLO_NUTRI_FIELDS;
                $sub_keys = ['nasycene_mk', 'cukry'];
                $skip_keys = ['energie_kj', 'energie_kcal'];

                foreach ($fields as $key => $field):
                    if (in_array($key, $skip_keys)) continue;
                    $value = get_post_meta(get_the_ID(), '_jidlo_' . $key, true);
                    $is_sub = in_array($key, $sub_keys);
                    $row_color = ($has_donut && isset($color_map[$key])) ? $color_map[$key][0] : '';
                    $row_pct = ($has_donut && isset($color_map[$key])) ? round($color_map[$key][1]) : '';
                    $bg_style = $row_color ? ' style="background:' . $row_color . '15"' : '';
                ?>
                <tr<?php echo $is_sub ? ' class="sub"' : ''; ?><?php echo $bg_style; ?>>
                    <th><?php echo esc_html($field['label']); ?></th>
                    <td><?php echo $value !== '' ? esc_html($value) . ' ' . esc_html($field['unit']) : '—'; ?></td>
                    <?php if ($has_donut): ?>
                        <td class="nutri-pct"><?php echo $row_pct !== '' ? $row_pct . ' %' : ''; ?></td>
                    <?php endif; ?>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>

        <?php if ($has_donut):
            $o1 = 0;
            $o2 = $o1 + $p_bilk;
            $o3 = $o2 + $p_sach_rest;
            $o4 = $o3 + $p_cukry;
            $o5 = $o4 + $p_tuky_rest;
        ?>
        <div class="donut-section">
            <div class="donut-chart">
                <svg viewBox="0 0 42 42">
                    <circle cx="21" cy="21" r="15.9" fill="none" stroke="#e8e8e8" stroke-width="5"/>
                    <?php
                    $segments = [
                        [$p_bilk,      '#e05555', $o1],
                        [$p_sach_rest, '#5588dd', $o2],
                        [$p_cukry,     '#2255aa', $o3],
                        [$p_tuky_rest, '#eebb44', $o4],
                        [$p_nmk,       '#cc9922', $o5],
                    ];
                    foreach ($segments as $seg):
                        if ($seg[0] < 0.5) continue;
                        $dash = $seg[0];
                        $gap = 100 - $dash;
                        $offset = 100 - $seg[2] + 25;
                    ?>
                    <circle cx="21" cy="21" r="15.9" fill="none"
                        stroke="<?php echo $seg[1]; ?>" stroke-width="5"
                        stroke-dasharray="<?php echo round($dash, 1); ?> <?php echo round($gap, 1); ?>"
                        stroke-dashoffset="<?php echo round($offset, 1); ?>"/>
                    <?php endforeach; ?>
                </svg>
            </div>
        </div>
        <?php endif; ?>

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
