import pygame

from src.effects import FloatingText


def process_collisions(level):
    for laser in list(level.lasers_group):
        for enemy in pygame.sprite.spritecollide(laser, level.enemies_group, False):
            if not laser.alive() or not enemy.alive() or not laser.register_hit(enemy):
                continue
            destroyed = enemy.take_damage(laser.damage)
            if laser.kind == "pulse":
                level.detonate_pulse(laser, enemy.rect.center, primary=enemy)
            if destroyed and enemy.alive():
                level.destroy_enemy(enemy)
        if not laser.alive():
            continue

        for debris in pygame.sprite.spritecollide(laser, level.debris_group, False):
            if not laser.alive() or not debris.alive() or not laser.register_hit(debris):
                continue
            destroyed = debris.take_damage(laser.damage)
            if laser.kind == "pulse":
                level.detonate_pulse(laser, debris.rect.center, primary=debris)
            if destroyed and debris.alive():
                level.detonate_debris(debris)
        if laser.alive():
            level.mission.handle_player_laser(laser)

    if not level.player or level.player.health <= 0:
        return

    for _ in pygame.sprite.spritecollide(level.player, level.enemy_lasers_group, True):
        level.damage_player(12)

    for enemy in pygame.sprite.spritecollide(level.player, level.enemies_group, False):
        level.damage_player(28 if enemy is level.boss else 22)
        if enemy is not level.boss and enemy.alive():
            level.create_explosion(enemy.rect.center, (255, 90, 100), scale=enemy.explosion_scale)
            enemy.kill()

    for debris in pygame.sprite.spritecollide(level.player, level.debris_group, True):
        level.damage_player(18)
        level.create_explosion(debris.rect.center, (150, 165, 185), scale=0.8)

    for powerup in pygame.sprite.spritecollide(level.player, level.powerups_group, True):
        powerup.apply_effect(level.player)
        level.sound.play_pickup()
        level.text_group.add(FloatingText(
            level.player.rect.center, powerup.label, (80, 240, 190), level.ui.sub_font,
        ))
