# Database Schema

> **Source of Truth**: `Dump20250902.sql` (Snapshot: Sept 2025)
> **Database Name**: `costomenu`
> **Verified**: Yes (Structurally verified against SQL Dump)

## Security & Privacy Notes
> [!WARNING]
> **PII & Sensitive Data**: The `users` table contains Personally Identifiable Information (PII) such as `billing_tax_id` (AFM), `phone`, and `email`. Ensure strict access controls when querying this table.
> **Passwords**: The `password` column is `VARCHAR(255)`. Verify that these values are hashed (e.g., bcrypt) and never stored in plain text.

## SQL Schema
Structure extracted from `Dump20250902.sql`.

```sql
CREATE TABLE `dashboard_widgets` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `columns` text,
  `column_labels` text,
  `query_text` text,
  `parameters` text,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `distributors` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `description` longtext,
  `image` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKf1ofpcanbark437ouw18d1fh9` (`user_id`),
  CONSTRAINT `FKf1ofpcanbark437ouw18d1fh9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6539 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `equipments` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `description` longtext,
  `code` varchar(255) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `distributor_id` bigint(20) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKbhibe9jidsaepoo0pmbtono1h` (`distributor_id`),
  KEY `FKtfsmcg04xwj6dvh4fd9g6j15o` (`user_id`),
  CONSTRAINT `FKbhibe9jidsaepoo0pmbtono1h` FOREIGN KEY (`distributor_id`) REFERENCES `distributors` (`id`) ON DELETE SET NULL,
  CONSTRAINT `FKtfsmcg04xwj6dvh4fd9g6j15o` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13697 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `flyway_schema_history` (
  `installed_rank` int(11) NOT NULL,
  `version` varchar(50) DEFAULT NULL,
  `description` varchar(200) NOT NULL,
  `type` varchar(20) NOT NULL,
  `script` varchar(1000) NOT NULL,
  `checksum` int(11) DEFAULT NULL,
  `installed_by` varchar(100) NOT NULL,
  `installed_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `execution_time` int(11) NOT NULL,
  `success` tinyint(1) NOT NULL,
  PRIMARY KEY (`installed_rank`),
  KEY `flyway_schema_history_s_idx` (`success`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `ingredient_categories` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKlawovuqf7867nk4cq84ibnyab` (`user_id`),
  CONSTRAINT `FKlawovuqf7867nk4cq84ibnyab` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17255 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ingredient_costs` (
  `ingredient_id` bigint(20) NOT NULL,
  `distributor_id` bigint(20) NOT NULL,
  `active` bit(1) DEFAULT NULL,
  `unit_cost` double DEFAULT NULL,
  `pack_cost` double DEFAULT NULL,
  `pack_weight` double DEFAULT NULL,
  `pack_unit_id` bigint(20) DEFAULT NULL,
  `min_cost` double DEFAULT NULL,
  `max_cost` double DEFAULT NULL,
  `scrap_percent` double DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`distributor_id`,`ingredient_id`),
  KEY `FK36wp8t7qwe1qqj9vx890mjj1m` (`ingredient_id`),
  KEY `FKkrlrnvfhyyqhubbskiqnitbfp` (`pack_unit_id`),
  CONSTRAINT `FK36wp8t7qwe1qqj9vx890mjj1m` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKhfk6bpy1vcpvcoaulk1rop18n` FOREIGN KEY (`distributor_id`) REFERENCES `distributors` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKkrlrnvfhyyqhubbskiqnitbfp` FOREIGN KEY (`pack_unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ingredient_units` (
  `ingredient_id` bigint(20) NOT NULL,
  `unit_id` bigint(20) NOT NULL,
  `conversion` double DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`ingredient_id`,`unit_id`),
  KEY `FKowoqlgcpyuk3vw52f05a07qej` (`unit_id`),
  CONSTRAINT `FKowoqlgcpyuk3vw52f05a07qej` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKrt6melopbdfg3alcdab22yikn` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ingredients` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `unit_cost` double DEFAULT NULL,
  `pack_weight` double DEFAULT NULL,
  `pack_unit_id` bigint(20) DEFAULT NULL,
  `pack_cost` double DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  `base_unit_id` bigint(20) DEFAULT NULL,
  `scrap_percent` double DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK4m7uffv0xjoh2ymuim0639plg` (`base_unit_id`),
  KEY `FK46dx9s4kupwjqntrw7301d1rb` (`category_id`),
  KEY `FKp4ty9l70hiukqe8eod9orgpj2` (`pack_unit_id`),
  KEY `FK3c7wmxbd9aqoh9hluau9wvwy1` (`user_id`),
  CONSTRAINT `FK3c7wmxbd9aqoh9hluau9wvwy1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FK46dx9s4kupwjqntrw7301d1rb` FOREIGN KEY (`category_id`) REFERENCES `ingredient_categories` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FK4m7uffv0xjoh2ymuim0639plg` FOREIGN KEY (`base_unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKp4ty9l70hiukqe8eod9orgpj2` FOREIGN KEY (`pack_unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=258828 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ingredients_backup` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `unit_cost` double DEFAULT NULL,
  `pack_weight` double DEFAULT NULL,
  `pack_unit_id` bigint(20) DEFAULT NULL,
  `pack_cost` double DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  `base_unit_id` bigint(20) DEFAULT NULL,
  `scrap_percent` double DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK4m7uffv0xjoh2ymuim0639plg` (`base_unit_id`),
  KEY `FK46dx9s4kupwjqntrw7301d1rb` (`category_id`),
  KEY `FKp4ty9l70hiukqe8eod9orgpj2` (`pack_unit_id`),
  KEY `FK3c7wmxbd9aqoh9hluau9wvwy1` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=250784 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `inventory_counts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `total` double DEFAULT NULL,
  `date` date DEFAULT NULL,
  `ingredients` text,
  `changes` text,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKn19xiy4d5q83ihj0vtbwurpe7` (`user_id`),
  CONSTRAINT `FKn19xiy4d5q83ihj0vtbwurpe7` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=409 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `invoices` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `invoice_number` varchar(255) DEFAULT NULL,
  `distributor_id` bigint(20) DEFAULT NULL,
  `amount` double DEFAULT NULL,
  `date` date DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKel87kgbfhaab5pb30jos7ot3n` (`distributor_id`),
  KEY `FKbwr4d4vyqf2bkoetxtt8j9dx7` (`user_id`),
  CONSTRAINT `FKbwr4d4vyqf2bkoetxtt8j9dx7` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKel87kgbfhaab5pb30jos7ot3n` FOREIGN KEY (`distributor_id`) REFERENCES `distributors` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=27464 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `licenses` (
  `id` bigint(20) NOT NULL,
  `duration` int(11) NOT NULL,
  `features` text,
  `name` varchar(255) DEFAULT NULL,
  `period` varchar(255) DEFAULT NULL,
  `price` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `lifetime_offer_members` (
  `offer_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`offer_id`,`user_id`),
  KEY `FKpscql831d8tvukuscfh2r8la8` (`user_id`),
  CONSTRAINT `FKpb0h2mvrh7ftj2wqd6lqx5twd` FOREIGN KEY (`offer_id`) REFERENCES `offers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKpscql831d8tvukuscfh2r8la8` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `menu_categories` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKin7oc15xlo23nsps3odm3pbcf` (`user_id`),
  CONSTRAINT `FKin7oc15xlo23nsps3odm3pbcf` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4059 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `menu_items` (
  `menu_id` bigint(20) NOT NULL,
  `recipe_id` bigint(20) NOT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `line_number` int(11) NOT NULL,
  `is_choice` bit(1) NOT NULL,
  `description` text,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`menu_id`,`recipe_id`),
  KEY `FK4pc1grgsms7nqm2i6oig37pro` (`category_id`),
  KEY `FKoupkyms1cjcs47stah0f1nlnw` (`recipe_id`),
  CONSTRAINT `FK4pc1grgsms7nqm2i6oig37pro` FOREIGN KEY (`category_id`) REFERENCES `menu_categories` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FK6fwmu1a0d0hysfd3c00jxyl2c` FOREIGN KEY (`menu_id`) REFERENCES `menus` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKoupkyms1cjcs47stah0f1nlnw` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `menus` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKrufxapib25ap0wmq1aaquppw6` (`user_id`),
  CONSTRAINT `FKrufxapib25ap0wmq1aaquppw6` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2738 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `messages` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `english_text` text,
  `greek_text` text,
  `display` bit(1) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `offer_feature_modules` (
  `offer_id` bigint(20) NOT NULL,
  `license_id` bigint(20) NOT NULL,
  `module` varchar(255) NOT NULL,
  KEY `FKi1vekp5rhfp44r1rij8hylq0m` (`license_id`,`offer_id`),
  CONSTRAINT `FKi1vekp5rhfp44r1rij8hylq0m` FOREIGN KEY (`license_id`, `offer_id`) REFERENCES `offer_features` (`license_id`, `offer_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `offer_features` (
  `offer_id` bigint(20) NOT NULL,
  `license_id` bigint(20) NOT NULL,
  `discount_exact` double DEFAULT NULL,
  `discount_percent` double DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `duration_period` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`license_id`,`offer_id`),
  KEY `FK4ac4ql5oy9m869362wwcd074h` (`offer_id`),
  CONSTRAINT `FK4ac4ql5oy9m869362wwcd074h` FOREIGN KEY (`offer_id`) REFERENCES `offers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKdryr78igo6deg8fei5rjsbrex` FOREIGN KEY (`license_id`) REFERENCES `licenses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `offers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `type` varchar(31) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` text,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK9yilcimbeupq2lyrqr1nlrjyb` (`user_id`),
  CONSTRAINT `FK9yilcimbeupq2lyrqr1nlrjyb` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `password_reset` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `token` varchar(500) DEFAULT NULL,
  `expiry_date` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKj94hgy9v5fw1munb90tar2dfg` (`user_id`),
  CONSTRAINT `FKj94hgy9v5fw1munb90tar2scx` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1844 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `payments` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `payment_date` date DEFAULT NULL,
  `amount` double NOT NULL,
  `transaction_id` varchar(255) DEFAULT NULL,
  `payment_doc_send` bit(1) DEFAULT NULL,
  `payment_doc_name` varchar(255) DEFAULT NULL,
  `comments` text,
  `order_code` varchar(255) DEFAULT NULL,
  `payment_info` text,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKj94hgy9v5fw1munb90tar2eje` (`user_id`),
  CONSTRAINT `FKj94hgy9v5fw1munb90tar2eje` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1208 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `promo_codes` (
  `code` varchar(255) NOT NULL,
  `campaign_id` bigint(20) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`code`),
  KEY `FKnmgtprg0jamwj021bdxqww30s` (`campaign_id`),
  CONSTRAINT `FKnmgtprg0jamwj021bdxqww30s` FOREIGN KEY (`campaign_id`) REFERENCES `offers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipe_allergens` (
  `recipe_id` bigint(20) NOT NULL,
  `allergens` varchar(255) NOT NULL,
  KEY `FK15vy656x2584g6gg4kxbkv8wp` (`recipe_id`),
  CONSTRAINT `FK15vy656x2584g6gg4kxbkv8wp` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipe_categories` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKm2b8c4tli1alrerjpulcfkyil` (`user_id`),
  CONSTRAINT `FKm2b8c4tli1alrerjpulcfkyil` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15436 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipe_equipments` (
  `recipe_id` bigint(20) NOT NULL,
  `equipment_id` bigint(20) NOT NULL,
  KEY `FK5o2hq8efmr5ynrf3l87qiwpem` (`equipment_id`),
  KEY `FKg9un4ydrnqw8e53q7sft6sahr` (`recipe_id`),
  CONSTRAINT `FK5o2hq8efmr5ynrf3l87qiwpem` FOREIGN KEY (`equipment_id`) REFERENCES `equipments` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKg9un4ydrnqw8e53q7sft6sahr` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipe_ingredients` (
  `ingredient_id` bigint(20) NOT NULL,
  `recipe_id` bigint(20) NOT NULL,
  `ordinal` int(11) NOT NULL,
  `portion` double DEFAULT NULL,
  `portion_unit_id` bigint(20) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`ingredient_id`,`recipe_id`),
  KEY `FKjgm8htcyxdgn4vst9asdfs3r7` (`portion_unit_id`),
  KEY `FKcqlw8sor5ut10xsuj3jnttkc` (`recipe_id`),
  CONSTRAINT `FKcqlw8sor5ut10xsuj3jnttkc` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKgukrw6na9f61kb8djkkuvyxy8` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKjgm8htcyxdgn4vst9asdfs3r7` FOREIGN KEY (`portion_unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipe_ingredients_backup` (
  `ingredient_id` bigint(20) NOT NULL,
  `recipe_id` bigint(20) NOT NULL,
  `ordinal` int(11) NOT NULL,
  `portion` double DEFAULT NULL,
  `portion_unit_id` bigint(20) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`ingredient_id`,`recipe_id`),
  KEY `FKjgm8htcyxdgn4vst9asdfs3r7` (`portion_unit_id`),
  KEY `FKcqlw8sor5ut10xsuj3jnttkc` (`recipe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipe_tags` (
  `recipe_id` bigint(20) NOT NULL,
  `tag_id` bigint(20) NOT NULL,
  KEY `FKoqq73b50aa11i89asflll1rp5` (`recipe_id`),
  KEY `FKebfy96fo2pv9onnlfbderqyfm` (`tag_id`),
  CONSTRAINT `FKebfy96fo2pv9onnlfbderqyfm` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKoqq73b50aa11i89asflll1rp5` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipe_units` (
  `recipe_id` bigint(20) NOT NULL,
  `unit_id` bigint(20) NOT NULL,
  `conversion` double DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`recipe_id`,`unit_id`),
  KEY `FKsw53jv9joxbl6djetk7qeer17` (`unit_id`),
  CONSTRAINT `FK722nusq0yd1te1c321i4a0ulh` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKsw53jv9joxbl6djetk7qeer17` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `recipes` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `preparation_link` varchar(1000) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  `is_gluten_free` bit(1) NOT NULL,
  `is_vegan` bit(1) NOT NULL,
  `is_vegetarian` bit(1) NOT NULL,
  `instructions` text,
  `archived` bit(1) NOT NULL,
  `food_cost` double DEFAULT NULL,
  `garnish` text,
  `price` double DEFAULT NULL,
  `scrap_percent` double DEFAULT NULL,
  `serving` int(11) NOT NULL,
  `uncosted` bit(1) NOT NULL,
  `used_as_subrecipe` bit(1) DEFAULT NULL,
  `waiter_description` text,
  `weight` double DEFAULT NULL,
  `price_boundary` double DEFAULT NULL,
  `yield_portion` double DEFAULT NULL,
  `utensil_id` bigint(20) DEFAULT NULL,
  `vat_category_id` bigint(20) DEFAULT NULL,
  `yield_unit_id` bigint(20) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKccidske719qyb4cccvglda2vw` (`category_id`),
  KEY `FKlc3x6yty3xsupx80hqbj9ayos` (`user_id`),
  KEY `FKooaesvpjy8wx5xe8o904lg9ia` (`utensil_id`),
  KEY `FK58vlu2l17f7wjksatph253kki` (`vat_category_id`),
  KEY `FK39r0awscxqfymhtghdalihnfa` (`yield_unit_id`),
  CONSTRAINT `FK39r0awscxqfymhtghdalihnfa` FOREIGN KEY (`yield_unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FK58vlu2l17f7wjksatph253kki` FOREIGN KEY (`vat_category_id`) REFERENCES `vat_categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `FKccidske719qyb4cccvglda2vw` FOREIGN KEY (`category_id`) REFERENCES `recipe_categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `FKlc3x6yty3xsupx80hqbj9ayos` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKooaesvpjy8wx5xe8o904lg9ia` FOREIGN KEY (`utensil_id`) REFERENCES `utensils` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=99065 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sub_recipes` (
  `recipe_id` bigint(20) NOT NULL,
  `subrecipe_id` bigint(20) NOT NULL,
  `ordinal` int(11) NOT NULL,
  `portion` double DEFAULT NULL,
  `portion_unit_id` bigint(20) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`recipe_id`,`subrecipe_id`),
  KEY `FKim7h4sr0ec8jl9xkdh0c8k5o6` (`portion_unit_id`),
  KEY `FKpd2smpyvpy65bf7u0aa5v83cy` (`subrecipe_id`),
  CONSTRAINT `FKim7h4sr0ec8jl9xkdh0c8k5o6` FOREIGN KEY (`portion_unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKpd2smpyvpy65bf7u0aa5v83cy` FOREIGN KEY (`subrecipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKqh4vjpylr6xkskjrjn8vklueb` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `tags` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKpsynysaxl7cyw8mr5c8xevneg` (`user_id`),
  CONSTRAINT `FKpsynysaxl7cyw8mr5c8xevneg` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1682 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `units` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `is_base` bit(1) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKfw5d38asiy9syx5m1bjwclsl8` (`user_id`),
  CONSTRAINT `FKfw5d38asiy9syx5m1bjwclsl8` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3592 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user_activity` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `activity` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_activity_userid_idx` (`user_id`),
  CONSTRAINT `FK_user_activity_to_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=631414 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user_features` (
  `user_id` bigint(20) NOT NULL,
  `module` varchar(255) NOT NULL,
  `module_limit` int(11) DEFAULT NULL,
  `enabled` bit(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`module`,`user_id`),
  KEY `FKn1bl34rxkodll6hm0dmrdijx0` (`user_id`),
  CONSTRAINT `FKn1bl34rxkodll6hm0dmrdijx0` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user_feedback` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `message` text,
  `comments` text,
  `date` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKpc3t9erufv86ti7uqrf778or3` (`user_id`),
  CONSTRAINT `FKpc3t9erufv86ti7uqrf778or3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=252 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user_feedback_attachments` (
  `user_feedback_id` bigint(20) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  PRIMARY KEY (`image_url`,`user_feedback_id`),
  KEY `FKpx15omws57b7ya1oljyxpahlq` (`user_feedback_id`),
  CONSTRAINT `FKpx15omws57b7ya1oljyxpahlq` FOREIGN KEY (`user_feedback_id`) REFERENCES `user_feedback` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user_license_features` (
  `user_id` bigint(20) NOT NULL,
  `license_id` bigint(20) NOT NULL,
  `start_date` date NOT NULL,
  `module` varchar(255) NOT NULL,
  `module_limit` int(11) DEFAULT NULL,
  `enabled` bit(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`module`,`license_id`,`start_date`,`user_id`),
  KEY `FKjo00l6dontb0cb0fp92p60j8m` (`license_id`,`start_date`,`user_id`),
  CONSTRAINT `FKjo00l6dontb0cb0fp92p60j8m` FOREIGN KEY (`license_id`, `start_date`, `user_id`) REFERENCES `user_licenses` (`license_id`, `start_date`, `user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user_licenses` (
  `user_id` bigint(20) NOT NULL,
  `license_id` bigint(20) NOT NULL,
  `current` bit(1) NOT NULL,
  `promo_code` varchar(255) DEFAULT NULL,
  `campaign_id` bigint(20) DEFAULT NULL,
  `start_date` date NOT NULL,
  `expiration_date` date DEFAULT NULL,
  `payment_id` bigint(20) DEFAULT NULL,
  `comments` text,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`license_id`,`start_date`,`user_id`),
  KEY `FKh6twtmrdljqg49tep2aym2pcg` (`payment_id`),
  KEY `FKghqp329j6qmha7nnidabxilcv` (`promo_code`),
  KEY `FKfhgxv1alp6sj4unoq1u76jyox` (`campaign_id`),
  KEY `FKm49g4rkrhl6f9kfmp7ydbt2b8` (`user_id`),
  CONSTRAINT `FKfhgxv1alp6sj4unoq1u76jyox` FOREIGN KEY (`campaign_id`) REFERENCES `offers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKghqp329j6qmha7nnidabxilcv` FOREIGN KEY (`promo_code`) REFERENCES `promo_codes` (`code`) ON DELETE CASCADE,
  CONSTRAINT `FKh6twtmrdljqg49tep2aym2pcg` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKm49g4rkrhl6f9kfmp7ydbt2b8` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `FKoo0ma7tmdvac8edtfm3iqsm3h` FOREIGN KEY (`license_id`) REFERENCES `licenses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `user_logins` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `login_date` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_logins_userid_idx` (`user_id`),
  CONSTRAINT `FK_user_logins_to_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26891 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `users` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `surname` varchar(255) DEFAULT NULL,
  `role` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `email_verified` bit(1) NOT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `job` varchar(255) DEFAULT NULL,
  `other_job` varchar(255) DEFAULT NULL,
  `company` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `about_to_expire_mail` bit(1) NOT NULL,
  `activation_token` varchar(255) DEFAULT NULL,
  `billing_activity` varchar(255) DEFAULT NULL,
  `billing_address` varchar(255) DEFAULT NULL,
  `billing_city` varchar(255) DEFAULT NULL,
  `billing_tax_authority` varchar(255) DEFAULT NULL,
  `billing_tax_id` varchar(255) DEFAULT NULL,
  `billing_title` varchar(255) DEFAULT NULL,
  `billing_type` varchar(255) DEFAULT NULL,
  `billing_vat` int(11) DEFAULT NULL,
  `billing_zip` varchar(255) DEFAULT NULL,
  `description` text,
  `has_expired_mail` bit(1) NOT NULL,
  `show_whats_new` bit(1) NOT NULL DEFAULT b'1',
  `prefs` text,
  `website` varchar(255) DEFAULT NULL,
  `push_message_key` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6921 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `utensils` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `distributor_id` bigint(20) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `description` longtext,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKb9xaksw225p0ck6fkfgo7ejvy` (`distributor_id`),
  KEY `FKjos247srr165xs1qkf38c81u3` (`user_id`),
  CONSTRAINT `FKb9xaksw225p0ck6fkfgo7ejvy` FOREIGN KEY (`distributor_id`) REFERENCES `distributors` (`id`) ON DELETE SET NULL,
  CONSTRAINT `FKjos247srr165xs1qkf38c81u3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6007 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `vat_categories` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `vat` double DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKlx2l2j5k2lotyaymrc2jpb77c` (`user_id`),
  CONSTRAINT `FKlx2l2j5k2lotyaymrc2jpb77c` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1993 DEFAULT CHARSET=utf8mb4;
```

## External Data Sources

### CRM Data (`cleaned_costo_menu.csv`)
- **Source**: CSV Export
- **Columns**:
  - `User id`
  - `Fullname`
  - `Email`
  - `Phone`
  - `Company`
  - `License`
  - `ExpirationDate`
  - `License status`
  - `Last activity date`
  - `Recipe count`
  - `Ingredients count`
  - `Menus count`
  - `Distributors count`
  - `Registration date`
  - `Total payments amount`
  - `Days Since Last Activity`
  - `Customer Lifetime Value`

### Sales Data (`SalesExport_23_1_2026.xls`)
- **Source**: Viva Payments Export (HTML Table)
- **Key Columns**:
  - `Ημ/νία` (Date)
  - `E-mail`
  - `Περιγραφή Εμπόρου` (Description)
  - `Ποσό` (Amount)
  - `Κατάσταση` (Status - e.g., 'Επιτυχημένη')
