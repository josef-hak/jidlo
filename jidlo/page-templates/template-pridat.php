<?php
/* Template Name: Přidat potravinu */

get_header();

if (!is_user_logged_in()):
?>
    <div class="login-prompt">
        <h2>Přihlaste se pro přidání potraviny</h2>
        <?php wp_login_form(['redirect' => get_permalink()]); ?>
    </div>
<?php else: ?>

<div class="food-form">
    <h1>Přidat potravinu</h1>

    <div class="form-message" id="form-message"></div>

    <form id="food-form" enctype="multipart/form-data">

        <div class="form-group">
            <label for="food-photo">Fotka</label>
            <input type="file" id="food-photo" name="food_photo" accept="image/*" capture="environment">
            <img class="photo-preview" id="photo-preview" alt="Náhled">
        </div>

        <div class="form-group">
            <label for="food-title">Název potraviny *</label>
            <input type="text" id="food-title" name="food_title" required autocomplete="off">
        </div>

        <div class="form-group">
            <label for="food-brand">Značka / Výrobce</label>
            <input type="text" id="food-brand" name="food_brand" autocomplete="off">
        </div>

        <div class="form-group">
            <label for="food-category">Kategorie</label>
            <select id="food-category" name="food_category">
                <option value="">— Vyberte —</option>
                <?php
                $categories = get_terms([
                    'taxonomy'   => 'kategorie_potravin',
                    'hide_empty' => false,
                ]);
                if (!empty($categories) && !is_wp_error($categories)):
                    foreach ($categories as $cat): ?>
                        <option value="<?php echo esc_attr($cat->term_id); ?>">
                            <?php echo esc_html($cat->name); ?>
                        </option>
                    <?php endforeach;
                endif;
                ?>
            </select>
        </div>

        <div class="form-section-title">Nutriční hodnoty (na 100 g)</div>

        <?php
        $sub_keys = ['nasycene_mk', 'cukry'];
        foreach (JIDLO_NUTRI_FIELDS as $key => $field):
            $is_sub = in_array($key, $sub_keys);
        ?>
        <div class="form-group">
            <label for="jidlo_<?php echo $key; ?>"<?php echo $is_sub ? ' class="sub"' : ''; ?>>
                <?php echo esc_html($field['label']); ?>
            </label>
            <input type="number" step="0.01" min="0" inputmode="decimal"
                   id="jidlo_<?php echo $key; ?>"
                   name="jidlo_<?php echo $key; ?>">
            <span class="unit"><?php echo esc_html($field['unit']); ?></span>
        </div>
        <?php endforeach; ?>

        <div class="form-group">
            <label for="food-notes">Poznámky</label>
            <textarea id="food-notes" name="food_notes" rows="3"></textarea>
        </div>

        <button type="submit" class="btn btn-primary" id="submit-btn">Uložit potravinu</button>
    </form>
</div>

<?php endif; ?>

<?php get_footer(); ?>
