"""Our own help texts for the fields of the game's classes, derived from how the reimplementation
(``zax-decomp/reimpl/src/``, every function verified equal to Zax.exe) reads and uses each field.

Zax.exe has a help text for only 253 of its 1,639 registered fields (``exeschema.Schema.help``). ``HELP``
describes the others: what the field does in the game, its units and notable effects. ``CORRECTIONS`` adds a
note to exe help texts that the code contradicts or leaves incomplete. Keys are (registering class, field
name), as ``exeschema.Schema.field`` gives them in ``owner``; values are (evidence level, the addresses of the
functions that consume the field, the English text). Evidence: "confirmed" = read from the reimplementation,
"verified" = also observed in the game, "assumption" = inferred, the text says what is assumed. The texts are
our own words (no exe strings), marked for lupdate; ``help_text`` returns them translated.
"""
from __future__ import annotations

from .i18n import QT_TRANSLATE_NOOP, translate

HELP: dict[tuple[str, str], tuple[str, str, str]] = {
    ('CAIBase', 'Marked For Deletion'): ('confirmed', '0x4fadc0, 0x4fbae0, 0x46e800', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set when an AI has finished (or gives up, e.g. a companion without a leader). The '
        'owning object still updates it once more, then removes and deletes it; a marked AI is also skipped when '
        'other code looks for an AI of a class. Setting it to 1 in a level removes the AI right after its first '
        'update; leave it at 0.')),
    ('CAIBase', 'Broadcaster'): ('confirmed', '0x4fd190, 0x4fd1e0, 0x4fd180', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the AI\'s list of listeners (objects waiting for its messages such as "Delete"); it'
        ' is created with the first listener and deleted with the last. Leave unchanged in a level.')),
    ('CActionAI', 'Action'): ('confirmed', '0x56d130', QT_TRANSLATE_NOOP(
        'fieldhelp', "Action run once, on the object's first update after the AI starts; the object is both $Trigger and "
        '$Instigator. On the next update the AI reports itself done to the object\'s AIs ("AI done", which e.g. '
        'advances a CSeriesAI).')),
    ('CActionAI', 'Executed Action'): ('confirmed', '0x56d130, 0x56ce60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 once "Action" has run. With 1 in a level the action is skipped and the AI only '
        'reports itself done; reset to 0 when the AI is reset. Leave at 0.')),
    ('CAmbientSoundAI', 'Sound'): ('confirmed', '0x42dcb0, 0x42dc60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Looping ambient sound (entry of the sound list) that the AI adds to the object's layer and starts on its"
        ' first update. If the layer cannot take it, the field is cleared and nothing plays; changing it removes '
        'a sound already playing.')),
    ('CAmbientSoundAI', 'Ambient Inner Radius'): ('confirmed', '0x42dcb0, 0x42db80, 0x4ee6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Radius in pixels around the object inside which the listener hears the sound centred (no direction). '
        "Beyond it the sound is played from the object's position.")),
    ('CAmbientSoundAI', 'Ambient Outer Radius'): ('confirmed', '0x42dcb0, 0x42dbc0, 0x4ee6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Extra distance in pixels beyond the inner radius at which the sound still plays at full volume: inner + '
        "outer radius is the sound's minimum (full-volume) distance.")),
    ('CAmbientSoundAI', 'Max Distance'): ('confirmed', '0x42dcb0, 0x42dc10, 0x4ee6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Fall-off distance in pixels added to inner + outer radius: the sound fades out over this range and is '
        'muted beyond inner + outer radius + max distance.')),
    ('CAmbientSoundAI', 'Layer Sound Handle'): ('confirmed', '0x42dcb0, 0x42dc60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: index of the sound in the layer's ambient sound list, -1 while none is added. A "
        'value other than -1 in a level stops the AI from ever adding and starting its sound; leave at -1.')),
    ('CApproachTargetAI', 'Move Behavior'): ('confirmed', '0x42e580, 0x42e5d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded movement behaviour (move-to-position) that walks the character towards its current target; its '
        'own fields (play ratio, path finding, smooth turning) control how it walks.')),
    ('CApproachTargetAI', 'Stop Distance'): ('confirmed', '0x42e5d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Distance in pixels from the target at which the character stops approaching; each new move aims at the '
        'point on the line to the target this far away from it. Default 150.')),
    ('CApproachTargetAI', 'Move Revision Frequency'): ('confirmed', '0x42e5d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Despite the name a period: seconds between two recalculations of the walk destination while the target '
        'is farther than the stop distance. Default 2.')),
    ('CApproachTargetAI', 'Time To Next Move Revision'): ('confirmed', '0x42e580, 0x42e5d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until the walk destination is recalculated; set to 0 when the AI starts. '
        'Leave unchanged in a level.')),
    ('CNormalAttackAI', 'Shoot Behavior'): ('confirmed', '0x523150, 0x5232c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Embedded shooting behaviour that fires the character's current weapon at its target. The AI alternates 1"
        " s shooting phases (only while the target is within the item's reach) with 3 s waiting phases.")),
    ('CNormalAttackAI', 'Turn Behavior'): ('confirmed', '0x523150, 0x5232c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Embedded behaviour that keeps pointing the character's weapon at its target; it runs on every update, "
        'also while waiting or moving.')),
    ('CNormalAttackAI', 'MoveBehavior'): ('confirmed', '0x523150, 0x5232c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Optional move-to-position behaviour used to reposition between shots. Without one (or with Minimum '
        'Attack Distance 0) the character attacks from where it stands.')),
    ('CNormalAttackAI', 'Minimum Attack Distance'): ('confirmed', '0x5232c0, 0x523150', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Distance in pixels the character tries to keep from its target: every 0.5 s while moving it heads for '
        'the point on the line to the target this far from it. 0 means it does not move while attacking. Default '
        '100.')),
    ('CNormalAttackAI', 'Move Buffer Zone'): ('confirmed', '0x5231d0, 0x5232c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Extra distance in pixels for random repositioning: when no path to the planned spot is found, or the '
        'movement stops while waiting, the character picks a random spot around the target at a distance up to '
        'minimum distance + buffer zone (lower bound the sum minus 1, but at most 100). Default 50.')),
    ('CNormalAttackAI', 'Waiting For Threshold'): ('confirmed', '0x522da0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only saved and loaded; no code of the game reads or writes it. No effect.')),
    ('CStandStillAttackAI', 'Shoot Behavior'): ('confirmed', '0x5859f0, 0x585a30', QT_TRANSLATE_NOOP(
        'fieldhelp', "Embedded shooting behaviour that fires the character's weapon at its target every update; the character "
        'stands still (walking characters are set to standing speed when the AI starts).')),
    ('CStandStillAttackAI', 'Turn Behavior'): ('confirmed', '0x5859f0, 0x585a30', QT_TRANSLATE_NOOP(
        'fieldhelp', "Embedded behaviour that keeps pointing the character's weapon at its target on every update.")),
    ('CBehaviorActivity', 'Behavior Queue'): ('confirmed', '0x42f610', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded queue of entity behaviours that the object runs one after another (only for animated objects). '
        'When the queue is empty the AI reports "AI done" to the object\'s AIs on every update.')),
    ('CCameraTrakerAI', 'Active'): ('confirmed', '0x5aa510', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the view follows the object on every update; 0: the AI does nothing. Default 1.')),
    ('CCameraTrakerAI', 'Camera Speed'): ('confirmed', '0x5aa510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Maximum speed in pixels per second at which the view target moves towards the object. 0 ("Immediately") '
        "or a target within one step's reach makes it jump there at once.")),
    ('CCameraTrakerAI', 'Got Caught Up'): ('confirmed', '0x5aa510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set to 1 once the view has reached the object; nothing reads it. Leave unchanged.')),
    ('CCameraTrakerAI', 'Camera Tracking Mode'): ('confirmed', '0x5aa510, 0x4f5dd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the view follows the view target: "Exact" centres the screen on it; "Stay Within Rect" scrolls only '
        'as far as needed to keep it inside the screen rectangle given by the rules; "Gradual" (default) does the'
        ' same but eases the target in smoothly (outside a network game or on the server).')),
    ('CCompanionAI', 'Move Behavior'): ('confirmed', '0x46e800, 0x46e890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move-to-position behaviour that flies the companion (a CEntityFlying, e.g. the drone) to a spot'
        ' near its leader, the object that created it.')),
    ('CCompanionAI', 'Minimum Distance'): ('confirmed', '0x46ead0, 0x46e890', QT_TRANSLATE_NOOP(
        'fieldhelp', "Smallest distance in pixels from the leader for the companion's next spot (random between minimum and "
        "maximum). Original bug: the spot's y is always the leader's y + 1, so the spread is only horizontal. "
        'Default 25.')),
    ('CCompanionAI', 'Maximum Distance'): ('confirmed', '0x46ead0, 0x46e890', QT_TRANSLATE_NOOP(
        'fieldhelp', "Largest distance in pixels from the leader for the companion's next spot (random between minimum and "
        'maximum; only horizontal because of an original bug). Default 50.')),
    ('CCompanionAI', 'Time Between Rechecks'): ('confirmed', '0x46e890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds between two choices of a new spot near the leader. Default 1.')),
    ('CCompanionAI', 'Time To Next Recheck'): ('confirmed', '0x46e800, 0x46e890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until the next spot is chosen; set to 0 when the AI starts. Leave '
        'unchanged.')),
    ('CCompanionAI', 'Attack Distance'): ('confirmed', '0x46e380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only saved and loaded; no code reads it. The companion attacks any target it can see, regardless of '
        'distance. No effect.')),
    ('CCompanionAI', 'Attack AI'): ('confirmed', '0x46e890, 0x46e800', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Attack AI (default CNormalAttackAI) the companion runs while its current target is visible to it.')),
    ('CCompanionAI', 'Set Target Behavior'): ('confirmed', '0x46e890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded behaviour that picks the closest target each update; the AI overwrites its search flags every '
        'update. Run-time state; leave unchanged.')),
    ('CDamageExpandingRadiusAI', 'Damage'): ('confirmed', '0x476b60, 0x476b20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage per second dealt to every destructable object inside the current radius (multiplied by the frame '
        'time each update). Default 100.')),
    ('CDamageExpandingRadiusAI', 'Damage Type'): ('confirmed', '0x476b60, 0x476b20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage type (from the damage type list) of the damage dealt; default "Unavoidable".')),
    ('CDamageExpandingRadiusAI', 'Damage Creator'): ('confirmed', '0x476b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Meant to choose whether the damage is credited to the object's creator or to the object; in the code "
        'both settings do the same (the creator is always used). No effect.')),
    ('CDamageExpandingRadiusAI', 'Use Animation For Radius'): ('confirmed', '0x476b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 (default): the radius is half the width of the object's current animation frame and the YX ratio is "
        "the frame's height over its width; Start/End Radius, Start To End Time and YX Ratio are then ignored. 0:"
        ' the radius grows from Start to End Radius.')),
    ('CDamageExpandingRadiusAI', 'Start Radius'): ('confirmed', '0x476b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal damage radius in pixels at the start (with Use Animation For Radius off). Default 10.')),
    ('CDamageExpandingRadiusAI', 'End Radius'): ('confirmed', '0x476b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal damage radius in pixels reached after Start To End Time; it stays there as long as the object'
        ' lives (with Use Animation For Radius off). Default 100.')),
    ('CDamageExpandingRadiusAI', 'YX Ratio'): ('confirmed', '0x476b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Vertical-to-horizontal ratio of the damage oval (the default 0.713 matches the game's perspective). "
        'Overwritten every update when Use Animation For Radius is on.')),
    ('CDamageExpandingRadiusAI', 'Start To End Time'): ('confirmed', '0x476b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds over which the radius grows linearly from Start Radius to End Radius (with Use Animation For '
        'Radius off). Default 2.')),
    ('CDoorAI', 'Is Locked'): ('confirmed', '0x4825b0, 0x482710, 0x4824a0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the door refuses every open, close and toggle request. Lock/unlock door actions change it and run '
        'After Locked / After Unlocked.')),
    ('CDoorAI', 'Allow Open or Close?'): ('confirmed', '0x4825b0, 0x482710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Optional condition action asked before every open or close (door object as $Trigger and $Instigator); if'
        ' it fails, the door stays as it is.')),
    ('CDoorAI', 'Before Open'): ('confirmed', '0x4825b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the door starts opening (from closed or while closing), before the opening sound and '
        'animation.')),
    ('CDoorAI', 'After Opened'): ('confirmed', '0x482170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the opening animation has finished and the door is open.')),
    ('CDoorAI', 'Before Closed'): ('confirmed', '0x482710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the door starts closing (from open or while opening).')),
    ('CDoorAI', 'After Closed'): ('confirmed', '0x482170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the closing animation has finished and the door is closed.')),
    ('CDoorAI', 'After Locked'): ('confirmed', '0x4824a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when a lock request locks a door that was unlocked.')),
    ('CDoorAI', 'After Unlocked'): ('confirmed', '0x4824a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when an unlock request unlocks a door that was locked.')),
    ('CDoorAI', 'Auto-Close Timeout'): ('confirmed', '0x482170, 0x4825b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds an open door stays open before it closes by itself; 0 (default) means never. Another open '
        'request on an open door restarts the countdown.')),
    ('CDoorAI', 'State'): ('confirmed', '0x482110, 0x482170, 0x4824a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: Closing, Closed, Opening, Open or Unknown (default). At the start it is taken from'
        ' the door\'s sequence ("Open" or "Closed"); a door left Unknown ignores open/close requests. Leave '
        'unchanged.')),
    ('CDoorAI', 'Timeout Time Left'): ('confirmed', '0x482170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left until an open door closes by itself (with Auto-Close Timeout above '
        '0). Leave unchanged.')),
    ('CDoorAI', 'Frame Andvance'): ('confirmed', '0x482170, 0x4825b0, 0x482710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: frames per second of the running opening/closing animation (negative when it runs '
        'backwards, 0 when the door is at rest). Leave unchanged.')),
    ('CDoorAI', 'Next Pain'): ('confirmed', '0x482170, 0x482710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until a closing door next hurts what it touches (every 0.2 s, by the '
        "model's closing damage × 0.2), -1 when it hurts nobody. Leave unchanged.")),
    ('CDoorAI', 'Triggered By Players'): ('confirmed', '0x481920', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only saved and loaded; the door code never reads it. Doors open only through actions and messages. No '
        'effect.')),
    ('CDoorAI', 'Triggered By Enemies'): ('confirmed', '0x481920', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only saved and loaded; the door code never reads it. No effect.')),
    ('CDrawTimeoutOvalAI', 'Radius'): ('confirmed', '0x4cad40', QT_TRANSLATE_NOOP(
        'fieldhelp', "Horizontal radius in pixels of the oval the AI's debug drawing shows; the debug drawing is never reached"
        ' in the release game. No effect in the game.')),
    ('CDrawTimeoutOvalAI', 'Aspect Ratio'): ('assumption', '0x4cad40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height-to-width ratio of the oval of the debug drawing, which the release game never shows. No effect in'
        ' the game.')),
    ('CDrawTimeoutOvalAI', 'Seconds Left'): ('confirmed', '0x4cae00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds until the object dies (removed as if killed); counts down every update. A negative value stops '
        'the countdown. Default 1.')),
    ('CDrawTimeoutRectAI', 'Seconds Left'): ('confirmed', '0x4cb1f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds until the object dies (removed as if killed); counts down every update. A negative value stops '
        'the countdown. Default 1.')),
    ('CFireContinuousFireWeaponBaseAI', 'Weapon Definition Index'): ('confirmed', '0x4735c0, 0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Item definition (from the item catalogue) of the continuous-fire weapon this AI fires; the carrier's "
        'matching weapon item provides the muzzle flash, and the definition gives range, damage, energy use, '
        'impact explosion and looping sound. The game adds this AI itself while such a weapon fires.')),
    ('CFireContinuousFireWeaponBaseAI', 'Impact Explosion'): ('confirmed', '0x4735c0, 0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the impact effect object the AI spawns at start and moves to the beam's hit point "
        '(shown only while something is hit). Leave unchanged.')),
    ('CFireContinuousFireWeaponBaseAI', 'Gun Item'): ('confirmed', '0x4735c0, 0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the carrier's weapon item found at start. Without it the AI ends at once. Leave "
        'unchanged.')),
    ('CFireContinuousFireWeaponBaseAI', 'Damaged Message Name'): ('confirmed', '0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the message sent to each object the beam damages, once per update while it is hit; AIs of the '
        'victim (e.g. a message handler) can react to it.')),
    ('CFireContinuousFireWeaponBaseAI', 'Muzzel Flash Entity'): ('confirmed', '0x474460, 0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the weapon's muzzle flash object the AI listens to; the beam starts there. If it "
        'dies or is deleted the AI ends. Leave unchanged.')),
    ('CFireContinuousFireWeaponBaseAI', 'Updates Since I Got IMoved Message'): ('confirmed', '0x4737c0, 0x474460', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: updates since the muzzle flash last reported "I Moved"; after more than 6 the AI '
        'ends and the weapon stops firing. Leave unchanged.')),
    ('CFireElectricalWeaponAI', 'Lightning To Use'): ('confirmed', '0x474d70, 0x474dc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Lightning object used as template; a copy is attached to the shooter at start and drawn from the muzzle '
        "to the hit point, or with random length and direction within the weapon's spread when nothing is hit.")),
    ('CFireElectricalWeaponAI', 'Lightning Path'): ('confirmed', '0x474d70, 0x475150', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the copy of the lightning attached to the shooter; it dies when the AI is '
        'deactivated. Leave unchanged.')),
    ('CFireElectricalWeaponAI', 'Clipped Message Name'): ('confirmed', '0x474dc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the message sent to an object that cuts off a missed lightning bolt (the bolt ends at it).')),
    ('CFireParticleWeaponAI', 'Particle System'): ('confirmed', '0x475750, 0x4757a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Particle system AI used as template; a copy is added to the muzzle flash at start, and its particle life'
        " is set each update so the particles reach the hit point or the weapon's range.")),
    ('CFireParticleWeaponAI', 'Particle System On Muzzel Flash'): ('confirmed', '0x475750, 0x475a50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the copy of the particle system on the muzzle flash; when it is deleted the AI '
        'ends. Leave unchanged.')),
    ('CFireParticleWeaponAI', 'Clipped Message Name'): ('confirmed', '0x4757a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the message sent to an object that cuts off the particle beam when nothing is hit (the beam ends'
        ' at it).')),
    ('CBounceAI', 'Bounce Dampen'): ('confirmed', '0x467400', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Share of the vertical speed kept when the object hits the ground (height below 0): it is put back to '
        'height 0 and a downward speed is reversed and multiplied by this value. 0..1, default 0.5.')),
    ('CBroadcastEvilAI', 'Evil To Broadcast'): ('confirmed', '0x585140, 0x584d40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Added on every update (per frame, not per second, so it depends on the frame rate) to the charge of '
        "Sphere of Zin items in the same layer, weighted by the rules' evil unit divided by the squared distance.")),
    ('CHandleMessageAI', 'Message To Handle'): ('confirmed', '0x4cd4f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the AI message (e.g. a "Damaged Message Name" or a message sent by an action) this AI reacts to;'
        ' matching messages run "Action" and count as handled.')),
    ('CHandleMessageAI', 'Action'): ('confirmed', '0x4cd4f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the message arrives; the object is $Trigger and $Instigator.')),
    ('CLightBeamAI', 'Player Damage On Collide'): ('confirmed', '0x4fe5f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage (hit points per collision) dealt to a destructable object touching the beam, meant for players. '
        'Original bug: the check only tests that the other object has any flags, so this value is used for '
        'practically every object. Default 1.')),
    ('CLightBeamAI', 'Enemy Damage On Collide'): ('confirmed', '0x4fe5f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage (hit points per collision) meant for non-player objects touching the beam. Because of an original'
        ' bug it applies only to objects without any flags, so in practice it is almost never used. Default 100.')),
    ('CPickupAI', 'Normal Item'): ('confirmed', '0x53e4c0, 0x53e110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Item definition (item catalogue) whose default item the pickup gives. With "!None" the "Special Item" is'
        ' given instead; a COverridePickupAI\'s "Item" on the object takes precedence over both.')),
    ('CPickupAI', 'Special Item'): ('confirmed', '0x53e4c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Inventory item object owned by the pickup, given when "Normal Item" is "!None" (or its definition is not'
        ' an item definition).')),
    ('CPickupAI', 'Alternate Item Def'): ('confirmed', '0x53e110, 0x53dea0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A COverridePickupAI on the object can replace or disable it.')),
    ('CPickupAI', 'Pickup Effect'): ('confirmed', '0x53e110', QT_TRANSLATE_NOOP(
        'fieldhelp', "Explosion/effect model spawned at the pickup's position when it is collected; empty = none.")),
    ('CPickupAI', 'Who Can Pick Up'): ('confirmed', '0x53e110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Categories (flags, default "Player") of objects that collect the pickup on touch; other objects touch it'
        ' without collecting.')),
    ('CPickupAI', 'Picked Up Action'): ('confirmed', '0x53e110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Runs right after the item (or the alternate item) is given, before the pickup disappears; the pickup is '
        '$Trigger and the collector $Instigator.')),
    ('CPickupAI', 'Show in HUD'): ('confirmed', '0x53e110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shows the item actually given (the alternate item if that was taken), for the collecting player.')),
    ('CPlaySequenceLoopedAI', 'Behavior'): ('confirmed', '0x4cb590, 0x4cb5c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Embedded looped-sequence behaviour that plays the object's sequence (with its fps, direction, ping-pong "
        'and loop settings); only for animated objects.')),
    ('CPlaySequenceLoopedAI', 'Stop Action'): ('confirmed', '0x4cb5c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action (default CSendAIDoneMessage) run when the behaviour reports it has finished, and again on every '
        'later update while it stays finished; the object is $Trigger and $Instigator.')),
    ('CSimpleCollideTriggerAI', 'Action'): ('confirmed', '0x571430', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time a matching object collides with this object; this object is $Trigger, the touching '
        'object $Instigator. There is no once-only limit.')),
    ('CSimpleCollideTriggerAI', 'Triggered By Anything'): ('confirmed', '0x571430', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: any colliding object fires the action, regardless of the other switches. Default 0.')),
    ('CSimpleCollideTriggerAI', 'Triggered By Players'): ('confirmed', '0x571430', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: objects of the player category fire the action. Default 1.')),
    ('CSimpleCollideTriggerAI', 'Triggered By Enemies'): ('confirmed', '0x571430', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: objects of the enemy category fire the action. Default 0.')),
    ('CSimpleCollideTriggerAI', 'Triggered By Projectiles'): ('confirmed', '0x571430', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: shots (objects with a CShotAI) fire the action. Default 0.')),
    ('CForceUpdatingAI', 'AI To Force'): ('confirmed', '0x4ccb60, 0x4ccc10, 0x4ccb90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The AI this wrapper runs; start, updates, messages and collisions are passed on to it. The wrapper also '
        "keeps the object updated even when it is outside every player's view.")),
    ('CForceUpdatingAI', 'Updated Radius'): ('confirmed', '0x4ccb60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Despite the "Depricated" group it is used: half width and half height in pixels of the square around the'
        ' object in which all objects keep updating when off screen; 0 updates only the object itself. A '
        '"deactivate AI" message ends this. Default 10.')),
    ('CGeneratorAI', 'Max Simultaneous'): ('confirmed', '0x4d08e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Largest number of generated objects alive at once: active objects in the layer named "New Name" '
        '(destructable ones only while they have hit points) plus pending generations. Default 1.')),
    ('CGeneratorAI', 'Delay Between Spawns'): ('confirmed', '0x4d0420, 0x4d0410', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds between two generation attempts; 0 or less stops the generator. Default 10.')),
    ('CGeneratorAI', 'Warp In'): ('confirmed', '0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default): a new animated object appears with the warp-in effect ("Warp Effect 1").')),
    ('CGeneratorAI', 'Things to Generate'): ('confirmed', '0x4d0520, 0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "List of spawnable entries; each generation picks one at random, weighted by the entries' weights, and "
        'centres the new object on the generator.')),
    ('CGeneratorAI', 'New Name'): ('confirmed', '0x4d08e0, 0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name given to every generated object; also used to count them for Max Simultaneous. Empty: the generator'
        ' never generates (it only reports an error).')),
    ('CGeneratorAI', 'Remove Default AIs'): ('confirmed', '0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the new object loses the AIs it comes with before "AIs to Add" are added. Default 0.')),
    ('CGeneratorAI', 'AIs to Add'): ('confirmed', '0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AIs copied onto every generated object.')),
    ('CGeneratorAI', 'After Action'): ('confirmed', '0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', '$Trigger is the generator object.')),
    ('CGeneratorAI', 'Time Till Next Generate'): ('confirmed', '0x4d0410, 0x4d0420', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until the next generation attempt; set to Delay Between Spawns when the '
        'generator starts. Leave unchanged.')),
    ('CGeneratorAI', 'Generations Pending'): ('confirmed', '0x4d0420, 0x4d08e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: generations postponed because a blocking object stood on the generator; one is '
        'retried per update. Leave at 0.')),
    ('CGeneratorAI', 'New Facing Angle'): ('confirmed', '0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Stored in radians, shown in degrees; only animated objects are turned.')),
    ('CGeneratorAI', 'Angle Variation'): ('confirmed', '0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Stored in radians, shown in degrees; the default 180° gives any direction.')),
    ('CGoToAI', 'Destination'): ('confirmed', '0x4d1b20, 0x4d15a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Name of the object to walk to (names like $Trigger work); it becomes the walker's current target while "
        'walking. Touching it also ends the walk.')),
    ('CGoToAI', 'Offset'): ('confirmed', '0x4d1b20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Offset in pixels (x, y) added to the destination's position.")),
    ('CGoToAI', 'Starting Action'): ('confirmed', '0x4d16b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run on the first update after the AI starts; the walker is $Trigger and $Instigator.')),
    ('CGoToAI', 'Finished'): ('confirmed', '0x4d1c90, 0x4d16b0, 0x4d1640', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 once the walk (and turn) is over; the AI then does nothing. Reset when the AI '
        'starts. Leave unchanged.')),
    ('CGoToAI', 'Move Finished'): ('confirmed', '0x4d16b0, 0x4d1c30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 while the walk is done and the final turn runs. Reset when the AI starts. Leave '
        'unchanged.')),
    ('CGoToAI', 'Failed Path'): ('confirmed', '0x4d1b20, 0x4d1ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 when no path to the destination was found; then "AI done" is sent instead of '
        'running "Done action". Reset when the AI starts. Leave unchanged.')),
    ('CGoToAI', 'Target Was Set By Goto AI'): ('confirmed', '0x4d1c90, 0x4d15e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: 1 while the walker's target is the destination set by this AI, so the AI clears it"
        ' again when done or deactivated. Leave unchanged.')),
    ('CGoToAI', 'Move Behavior'): ('confirmed', '0x4d1b20, 0x4d16b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move-to-position behaviour that walks the object to the destination (path finding, smooth '
        'turning, play ratio).')),
    ('CGoToAI', 'Done action'): ('confirmed', '0x4d1ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the walk (and the optional turn) is finished and a path was found; the walker is '
        '$Trigger and $Instigator. The AI does not end by itself, so this action usually sends "AI done".')),
    ('CGoToAI', 'Make New Home'): ('confirmed', '0x4d1c90', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: on arrival the walker's home position becomes its current position. Default 0.")),
    ('CGoToAI', 'Play Ratio'): ('confirmed', '0x4d1b20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Speed factor of the walk passed to the move behaviour; if the move behaviour's own play ratio is above 0"
        ' it overwrites this field when the walk starts.')),
    ('CGoToAI', 'Time To Try To Move'): ('confirmed', '0x4d16b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time timer: while walking it counts down; at 0 it is reset to 1 second and, if the move behaviour '
        'has stopped (speed 0), the walk is started again. Leave unchanged.')),
    ('CGoToAI', 'Set Facing Angle'): ('confirmed', '0x4d16b0, 0x4d1c30', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: after arriving, the walker turns to the angle of "Facing Angle" while playing "Turn Sequence Name". '
        'Default 0.')),
    ('CGoToAI', 'Turn Sequence Name'): ('confirmed', '0x4d1c30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence played from frame 0 during the final turn (with Set Facing Angle). Default "Idle".')),
    ('CGoToAI', 'Facing Angle'): ('confirmed', '0x4d1c30, 0x4d16b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded turn-to-angle behaviour used for the final turn; its "Angle To Turn To" is the facing after '
        'arrival.')),
    ('CGoToAI', 'Need to Call Start'): ('confirmed', '0x4d1640, 0x4d16b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 until the first update ran "Starting Action"; set to 1 when the AI starts. Leave'
        ' unchanged.')),
    ('CGravityAI', 'BounceAction'): ('confirmed', '0x4ca7b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the falling object hits Ground Height and the bounce does not already lift it within the'
        ' same step; the object is $Trigger and $Instigator.')),
    ('CGravityAI', 'Ground Height'): ('assumption', '0x4ca7b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height in pixels at which the falling object bounces (its vertical speed reversed and scaled by the '
        "model's bounce factor). The AI forces a constant fall speed of about 321.5 pixels per second. Default 0.")),
    ('CIdleAI', 'Idle Behavior'): ('confirmed', '0x4cc7d0, 0x4cc800', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded idle behaviour that lets an animated object stand and play its idle animation and fidgets. '
        'Run-time state of the behaviour; leave unchanged.')),
    ('CChaseInvestigateAI', 'AFloat'): ('confirmed', '0x46c0a0, 0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move behaviour (a CEntityBehaviorMoveToPos, despite the odd name) that walks the figure to the '
        'point to investigate; its own settings (path finding, play ratio, sequence) apply. When its Play Ratio '
        'is above 0 it also overrides this AI\'s "Play Ratio".')),
    ('CChaseInvestigateAI', 'Turn Behavior'): ('confirmed', '0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded turn behaviour used after arriving: the figure turns to face the investigated point before the '
        '"Investigate AI" starts (skipped when "Radius to Investigate Point" is 0). Also used to turn to the '
        "entity's own angle in the internal 'Going Home' state.")),
    ('CChaseInvestigateAI', 'Play Ratio'): ('confirmed', '0x46c0a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animation speed factor (1 = normal) passed to the move behaviour for the walk to the point. Before the '
        'move it is replaced by the embedded move behaviour\'s ("AFloat") Play Ratio whenever that is above 0, so '
        'in practice it mirrors that value.')),
    ('CChaseInvestigateAI', 'Next Try To Move'): ('confirmed', '0x46bfe0, 0x46c0a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: countdown in seconds to the next move attempt. It is reset to 0 at the start and '
        'set to 1 after the single move attempt; no later retry happens. Leave unchanged in a level.')),
    ('CChaseInvestigateAI', 'Time To Investigate'): ('confirmed', '0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds the figure spends investigating (running the "Investigate AI") once it has reached the point '
        '(default 5). Afterwards it switches back to walking and reports the target as lost, so the owning AI '
        '(e.g. the skeleton AI) gives up.')),
    ('CChaseInvestigateAI', 'Count To Investigate'): ('confirmed', '0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: remaining investigation time in seconds, copied from "Time To Investigate" on '
        'arrival and counted down. Leave unchanged in a level.')),
    ('CChaseInvestigateAI', 'Radius to Investigate Point'): ('confirmed', '0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Arrival distance in pixels (vertical distances stretched by about 1.4 for the perspective): the walk '
        'ends once the figure is this close to the point (or the move finishes). With 0 (default) the figure only'
        ' stops when the move ends and does not turn to face the point before investigating.')),
    ('CChaseInvestigateAI', 'Run To Investigate'): ('confirmed', '0x46bfe0, 0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default): a walking figure runs to the point; 0: it walks. After the investigation the gait is set '
        'back to walking.')),
    ('CChaseInvestigateAI', 'State'): ('confirmed', '0x46bfe0, 0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of the investigation (Chasing = walking to the point, Turning To Investigate, '
        'Investigating, Going Home, Turning, Done, Idle). It is reset to "Chasing" every time the AI begins; '
        'leave unchanged in a level.')),
    ('CChaseInvestigateAI', 'Investigate AI'): ('confirmed', '0x46c1c0, 0x46c660', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI run while investigating at the point, for "Time To Investigate" seconds; it must be a '
        'CInvestigateAreaAI kind (default CScanInvestigateAI, which looks around). Messages to this AI are passed'
        ' on to it. Empty: the figure just waits there.')),
    ('CTenaciousInvestigateAI', 'Move Revision Frequency'): ('confirmed', '0x58c620', QT_TRANSLATE_NOOP(
        'fieldhelp', "Seconds between re-aiming the move at the position of the entity's current target (default 2). The "
        'countdown only restarts when a target exists, so without one the AI checks again every frame.')),
    ('CTenaciousInvestigateAI', 'Move Behavior'): ('confirmed', '0x58c5d0, 0x58c620', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move behaviour that walks the figure towards its current target; path finding is switched on '
        'when the AI begins and each re-aim uses play ratio 1.')),
    ('CTenaciousInvestigateAI', 'Time To Next Move Revision'): ('confirmed', '0x58c5d0, 0x58c620', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until the next re-aim at the target; set to 0 when the AI begins, so the '
        'first re-aim happens at once. Leave unchanged in a level.')),
    ('CScanInvestigateAI', 'AI'): ('confirmed', '0x566390, 0x5663b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded CScanAreaAI that does the actual work: the figure sweeps its view back and forth between the '
        'scan angles while investigating. All begin, update and drawing calls are passed on to it.')),
    ('CLandscapeAI', 'Target Elevation'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Ground elevation (0–255, default 127) the terrain cells under the area are moved towards.')),
    ('CLandscapeAI', 'Width'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width in pixels (default 32) of the area around the object's position whose ground cells (64 × 64 pixels"
        ' each) are changed.')),
    ('CLandscapeAI', 'Height'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', "Height in pixels (default 32) of the area around the object's position whose ground cells are changed; "
        'for an "Oval" shape it sets the vertical squeeze of the ellipse.')),
    ('CLandscapeAI', 'Change Rate'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Elevation units per second each cell moves towards "Target Elevation" (default 40). Fractions are '
        'carried over between frames; the step is not clamped, so a high rate can overshoot the target. 0 means '
        'stopped; the AI itself sets it to 0 when "Stop When" is met.')),
    ('CLandscapeAI', 'Leftover Error'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the fraction of an elevation unit not yet applied, carried to the next frame. '
        'Leave unchanged in a level.')),
    ('CLandscapeAI', 'Shape'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', '"Rectangle" (default) changes every cell in the width × height area; "Oval" only the cells inside the '
        'ellipse fitting that area (with a margin of half a cell).')),
    ('CLandscapeAI', 'Stop When'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When the change stops (rate set to 0): "Any Point Reaches Target" (default) as soon as one cell is at '
        'the target; "All Points Reach Target" when no cell could be changed any more (all at the target or '
        'outside the limits); "Never" keeps running.')),
    ('CLandscapeAI', 'Do Not Modify If GreaterThan'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Cells whose current elevation is above this value (0–255, default 255) are left alone.')),
    ('CLandscapeAI', 'Do Not Modify If Less Than'): ('confirmed', '0x4e4060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Cells whose current elevation is below this value (0–255, default 0) are left alone.')),
    ('CLimitedTimeAI', 'What To Do'): ('confirmed', '0x4cd080, 0x4cd0a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The AI that runs for at most "Max Time" seconds; collisions and messages are passed to it only while '
        'time is left. Must be set: the begin call does not check for an empty field (the original crashes).')),
    ('CLimitedTimeAI', 'Max Time'): ('confirmed', '0x4cd080, 0x4cd0a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds the "What To Do" AI may run (default 1, up to 99999); the countdown restarts every time this AI '
        'begins.')),
    ('CLimitedTimeAI', 'Time Left'): ('confirmed', '0x4cd080, 0x4cd0a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds remaining, set from "Max Time" on begin. Leave unchanged in a level.')),
    ('CLimitedTimeAI', 'Done Action'): ('confirmed', '0x4cd0a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run once when the time is up (default CSendAIDoneMessage, which tells the owner the AI is done). '
        'Empty: nothing happens, the AI just stops.')),
    ('COldBadPatrolAI', 'Return Home Dist'): ('confirmed', '0x53b1f0, 0x53acf0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Distance in pixels from the entity's home point (vertical distances stretched by about 1.4); when the "
        'entity is farther away, its next random leg heads back towards home. 0 or below (default -1) switches '
        'this off.')),
    ('COverridePickupAI', 'Item'): ('confirmed', '0x53e4c0, 0x53efe0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Inventory item this pickup gives instead of the CPickupAI\'s own "Normal Item"/"Special Item". Empty: the'
        " CPickupAI's item is used.")),
    ('COverridePickupAI', 'Alternate Item Def'): ('confirmed', '0x53e110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set (not "!None") it replaces the CPickupAI\'s own "Alternate Item Def" for this object. The '
        'alternate item is offered whenever the main item refuses the character (its own acceptance check; '
        'already owning it is the usual reason).')),
    ('COverridePickupAI', 'Respawn Mode'): ('confirmed', '0x53da40, 0x53e110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'What happens after pickup. "Don\'t Respawn" (default): the object is deleted. Otherwise it is only hidden'
        ' and made non-collidable: "Respawn Delay After Pickup" brings it back "Respawn Delay" seconds after it '
        'was taken; "Respawn Regularly If Gone" brings it back at the next fixed respawn moment; "Respawn '
        'Regularly (Accumulate)" at every fixed moment brings it back or, if it is still there, drops an extra '
        'copy near it.')),
    ('COverridePickupAI', 'Respawn Delay'): ('confirmed', '0x53da40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds (0.01–86400, default 15): the wait after pickup in "Respawn Delay After Pickup" mode, and the '
        'interval between the fixed respawn moments in the two regular modes.')),
    ('COverridePickupAI', 'Min Respawn Delay'): ('confirmed', '0x53da40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds added to the start of the fixed respawn schedule in the two regular modes (moments = this + a '
        'random offset + multiples of "Respawn Delay"). Not used by "Respawn Delay After Pickup".')),
    ('COverridePickupAI', 'TimeUntilNextRespawn'): ('confirmed', '0x53d990, 0x53da40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until the next respawn, set to "Respawn Delay" when the pickup starts and '
        'updated every frame. Leave unchanged in a level.')),
    ('COverridePickupAI', 'Time Offset'): ('confirmed', '0x53d990, 0x53da40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: a random offset between 0 and "Respawn Delay" drawn when the pickup starts, so '
        'pickups with the same schedule do not all respawn at once. Leave unchanged in a level.')),
    ('COverridePickupAI', 'Last Simulation Time'): ('confirmed', '0x53d990, 0x53da40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: game time in seconds of the last respawn check, reset to 0 when the pickup starts.'
        ' Leave unchanged in a level.')),
    ('CParticleAI', 'X Center Pos'): ('confirmed', '0x52e2d0, 0x52a0d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X of the centre the particle moves around (used by the swirl particle). The particle system overwrites '
        'it with the emitter position when it creates the particle, so a value set here has no effect.')),
    ('CParticleAI', 'Y Center Pos'): ('confirmed', '0x52e2d0, 0x52a0d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y of the centre the particle moves around (used by the swirl particle). Overwritten with the emitter '
        'position when the particle system creates the particle.')),
    ('CParticleAI', 'Z Center Pos'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Height of the particle's centre. Overwritten with the emitter height when the particle system creates "
        'the particle; no particle AI reads it afterwards.')),
    ('CParticleAI', 'Animated'): ('confirmed', '0x528a40, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: the particle's animation frame follows its age, so the sequence plays once over the particle's "
        'lifetime (or at its own speed with "Obey Sequence FPS"). The particle system overwrites it with the '
        '"Animated" flag of the CParticleInfo entry.')),
    ('CParticleAI', 'Obey Sequence FPS'): ('confirmed', '0x528a40, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'With "Animated": 1 plays the sequence at its own frame rate, looping; 0 stretches it over the particle\'s'
        ' lifetime. Overwritten by the particle system from the CParticleInfo entry.')),
    ('CParticleAI', 'Y To X Ratio'): ('confirmed', '0x52a0d0, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Vertical squeeze of the swirl's circle (1 = the normal perspective oval). Overwritten by the particle "
        'system with the start point type\'s "YX Ratio" (1 without one); a 0 would divide by zero in the swirl.')),
    ('CGravityParticleAI', 'Gravity'): ('confirmed', '0x5292c0, 0x5293d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Downward acceleration of the particle (-100 to 100, default 9.8); multiplied by about 32.8 into world '
        'units per second². Negative values make particles rise.')),
    ('CGravityParticleAI', 'Bounce Sound'): ('confirmed', '0x529600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when the particle comes back above the ground after a bounce. Empty: silent bounces.')),
    ('CGravityParticleAI', 'Use Velocity to Advance Frames'): ('confirmed', '0x529320', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: the animation advances by the particle's horizontal speed (distance travelled divided by the "
        "sequence's frame rate) instead of by its age, so it stops animating when it stops moving.")),
    ('CGravityParticleAI', 'Bounced Last Frame'): ('confirmed', '0x529420, 0x529600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set by a bounce, cleared when the "Bounce Sound" is played. Leave unchanged in a '
        'level.')),
    ('CGravityParticleAI', 'Gravity Constant'): ('confirmed', '0x5292c0, 0x5293d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: "Gravity" converted to world units (times about 32.8), recomputed when the '
        'particle starts. Leave unchanged in a level.')),
    ('CSwirlParticleAI', 'Angular Velocity'): ('confirmed', '0x52a070, 0x52a0d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Speed at which the particle circles around its centre, stored in radians per second (the editor shows '
        'degrees; default 60°/s, range ±360°/s). Negative values turn the other way.')),
    ('CSwirlParticleAI', 'Angular Velocity Variance'): ('confirmed', '0x52a070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Random spread (±, sign ignored) added to "Angular Velocity" for each particle when it starts; same '
        'units.')),
    ('CSwirlParticleAI', 'Rotate Velocity'): ('confirmed', '0x52a0d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Meant to turn the particle's velocity along with the swirl, but the code only sets the unchanged "
        'velocity again, so it has no visible effect.')),
    ('CSwirlParticleAI', 'Current Angular Velocity'): ('confirmed', '0x52a070, 0x52a0d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: this particle\'s actual angular velocity ("Angular Velocity" ± the variance), drawn'
        ' when it starts. Leave unchanged in a level.')),
    ('CGenericParticleSystemAI', 'Outer Cone Angle'): ('confirmed', '0x52e2d0, 0x52eb40', QT_TRANSLATE_NOOP(
        'fieldhelp', "Envelope (degrees) for the random spread of the emission cone: each particle's angle from the cone axis "
        'is "Inner Cone Angle" plus a random value between 0 and this. Uses the start value, or the current value'
        ' when the envelope has a change speed.')),
    ('CGenericParticleSystemAI', 'Inner Cone Angle'): ('confirmed', '0x52e2d0, 0x52eb40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Envelope (degrees): the smallest angle between a particle\'s direction and the cone axis; "Outer Cone '
        'Angle" adds a random spread on top. 0 with no outer spread shoots all particles along the axis.')),
    ('CGenericParticleSystemAI', 'Face Angle'): ('confirmed', '0x52ebd0, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Envelope (degrees): horizontal direction the cone axis and the start shape point to; with "Orient To '
        'Parent\'s Rotation" it is added to the object\'s own facing.')),
    ('CGenericParticleSystemAI', 'Cone Trajectory'): ('confirmed', '0x52ebd0, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Envelope (degrees): vertical tilt of the cone axis (and the start shape), e.g. to shoot particles '
        'upwards or along the ground.')),
    ('CGenericParticleSystemAI', 'Burst Frequency'): ('confirmed', '0x52e220, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Bursts per second (default 1). The actual rate is redrawn from this ± "Burst Frequency Variance" at the '
        'start and after every emission; each burst emits the configured particles once.')),
    ('CGenericParticleSystemAI', 'Burst Frequency Variance'): ('confirmed', '0x52e220, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Random spread (± bursts per second) applied to "Burst Frequency" each time the rate is redrawn.')),
    ('CGenericParticleSystemAI', 'Num Bursts To Stop After'): ('confirmed', '0x52e2d0, 0x52eef0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of bursts after which the system switches itself off ("Enabled" 0); 0 = "Don\'t Stop". A "Particle'
        ' System On" message starts it again with a fresh count.')),
    ('CGenericParticleSystemAI', 'Start Point Type'): ('confirmed', '0x52e2d0, 0x52e220', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shape in which particles start around the emitter: point (default), line, disk, cylinder or sphere, each'
        ' with its own size settings; its "YX Ratio" is also passed to the particles. Empty: all start at the '
        'emitter point.')),
    ('CGenericParticleSystemAI', "Orient To Parent's Rotation"): ('confirmed', '0x52e080, 0x52ebd0, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: the position offsets, the emission direction and the particles' facing turn with the object's facing "
        'angle; 0 (default): they are fixed in the world.')),
    ('CGenericParticleSystemAI', 'X Offset'): ('confirmed', '0x52e080', QT_TRANSLATE_NOOP(
        'fieldhelp', "Horizontal offset of the emitter from the object's position, in pixels (-500 to 500).")),
    ('CGenericParticleSystemAI', 'Y Offset'): ('confirmed', '0x52e080', QT_TRANSLATE_NOOP(
        'fieldhelp', "Vertical (screen y) offset of the emitter from the object's position, in pixels (-500 to 500).")),
    ('CGenericParticleSystemAI', 'Height'): ('confirmed', '0x52e080', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height of the emitter above the ground in pixels (-500 to 500); for a game entity its own height is '
        'added unless the particles are children of the generator.')),
    ('CGenericParticleSystemAI', 'Speed'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Envelope for the particles\' start speed in pixels per second; "Speed Variance" adds a random spread.')),
    ('CGenericParticleSystemAI', 'Speed Variance'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Random spread (± pixels per second, 0–1000) added to each particle's start speed.")),
    ('CGenericParticleSystemAI', 'Age'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Envelope for the particles\' lifetime in seconds; "Age Variance" adds a random spread and the travel '
        'distance limits clamp it. A lifetime of 0 or less becomes 0.01 s.')),
    ('CGenericParticleSystemAI', 'Age Variance'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Random spread (± seconds, 0–100) added to each particle's lifetime.")),
    ('CGenericParticleSystemAI', 'Max Travel Distance'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Longest distance in pixels a particle may travel: its lifetime is shortened so that speed × lifetime '
        'does not exceed this (default 999999 = no limit).')),
    ('CGenericParticleSystemAI', 'Min Travel Distance'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shortest distance in pixels a particle travels: its lifetime is lengthened so that speed × lifetime '
        'reaches at least this (default 0 = no minimum).')),
    ('CGenericParticleSystemAI', 'Use Particle As Shot'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: each particle is created with the emitting object's top-most parent as its owner, like a shot fired "
        'by it (what that changes, e.g. who gets credited for damage, is assumed); 0: particles have no owner.')),
    ('CGenericParticleSystemAI', 'Make Child of Generator'): ('confirmed', '0x52e2d0, 0x52e080', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: particles become children of the emitting object and move along with it; 0 (default): they are added '
        'to the layer and stay where they were emitted.')),
    ('CGenericParticleSystemAI', 'Limit Duration To First Collision'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: each new particle is swept once through the layer's collision along its path and its remaining "
        'lifetime is then set to 0.1 s (meant for particles that end at the first obstacle; whether the sweep '
        'moves the particle is assumed).')),
    ('CGenericParticleSystemAI', 'Particles'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'List of particle kinds (CParticleInfo: model, particle AI, animation flags, count ± variance per burst, '
        'collision flags). Every burst emits each entry; with an empty list nothing is emitted.')),
    ('CGenericParticleSystemAI', 'NumBursts'): ('confirmed', '0x52e220, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the bursts accumulated but not yet emitted (a fraction below 1 between bursts); '
        'set to a random value in [0, 1) at start so systems do not fire in sync. Leave unchanged in a level.')),
    ('CGenericParticleSystemAI', 'CurFrequency'): ('confirmed', '0x52e220, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the current burst rate (bursts per second, despite the unit label) drawn from '
        '"Burst Frequency" ± variance. Leave unchanged in a level.')),
    ('CGenericParticleSystemAI', 'Enabled'): ('confirmed', '0x52e2d0, 0x52eef0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default): the system emits. 0: it stays silent until a "Particle System On" message; the system '
        'clears it itself on "Particle System Off" or when "Num Bursts To Stop After" is reached.')),
    ('CGenericParticleSystemAI', 'Disable in multi-player'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default): the system emits nothing while a game type is active that reports it should be off (a check'
        " of the game type, presumably 'multi-player'); 0: it always runs.")),
    ('CGenericParticleSystemAI', 'Choose Sound Based On Burst'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the sound from "Sounds" is picked by how many particles this emission produced relative to the '
        'maximum possible (more particles, later entry); 0 (default): picked at random.')),
    ('CGenericParticleSystemAI', 'Sounds'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sounds of which one is played at the emitter after each frame in which bursts were emitted. Empty: '
        'silent.')),
    ('CGuardPosAI', 'Idle Behavior'): ('confirmed', '0x586050, 0x586170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded idle behaviour (with fidgets) the guard runs while standing at its post; the "Idle" sequence is'
        ' started at normal speed each time idling begins.')),
    ('CGuardPosAI', 'Move To Behavior'): ('confirmed', '0x586050, 0x586170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move behaviour used to walk back to the post when the AI begins more than 5 pixels away from '
        "it; the figure walks (not runs), with this behaviour's Play Ratio as animation speed.")),
    ('CGuardPosAI', 'Going Home'): ('confirmed', '0x586050, 0x586170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 while the guard walks back to its post; recomputed every time the AI begins. '
        'Leave unchanged in a level.')),
    ('CGuardPosAI', 'Next Try To Move'): ('confirmed', '0x586170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time countdown in seconds: while above 0 it counts down and then restarts the guard behaviour. '
        'Nothing in the game sets it above 0, so a value set in a level only delays that restart; normally leave '
        'at 0.')),
    ('CGuardPosAI', 'Time Since Last Turn'): ('confirmed', '0x586170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds since idling began, counted up every frame but not used for anything else.'
        ' Leave unchanged in a level.')),
    ('CGuardPosAI', 'Turning'): ('confirmed', '0x586050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state without effect: only cleared when the AI begins and never set or read otherwise. '
        'Leave unchanged in a level.')),
    ('CPatrolAreaAI', 'Radius'): ('confirmed', '0x53b960, 0x53b930', QT_TRANSLATE_NOOP(
        'fieldhelp', "Radius in pixels (default 200) of the oval around the figure's home point in which random patrol points "
        'are chosen (vertically squeezed by the perspective factor 0.71). After four unreachable points it picks '
        'one near itself towards the home point, and waits 1 s if that fails too.')),
    ('CPatrolAreaAI', 'TimeOfLastChangeDirectionDueToCollide'): ('confirmed', '0x53b5f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved but unused: no code reads or writes it besides loading and saving.')),
    ('CPatrolAreaAI', 'Moving'): ('confirmed', '0x53b960, 0x53b830', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move behaviour that walks the figure to each patrol point; its Play Ratio is the animation '
        'speed. The figure is set to walking (not running) when the AI begins.')),
    ('CPatrolAreaAI', 'Retry New Point'): ('confirmed', '0x53b890, 0x53b960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left before a new patrol point is tried after no reachable point was found'
        ' (set to 1). Leave unchanged in a level.')),
    ('CPatrolPathAI', 'Path Poly'): ('confirmed', '0x53c5c0, 0x53c640', QT_TRANSLATE_NOOP(
        'fieldhelp', "Name of the level object whose polygon (at least 2 points) is the patrol path, looked up in the figure's"
        " layer when the AI begins. The points count relative to that object's position. Without a valid path the"
        ' figure does nothing.')),
    ('CPatrolPathAI', 'PathPolygonLayerPart'): ('confirmed', '0x53c5c0, 0x53c640', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the path object found by "Path Poly". Leave unchanged in a level.')),
    ('CPatrolPathAI', 'Order'): ('confirmed', '0x53c8d0, 0x53c7d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the points are visited, starting at the point nearest to the figure: "Back and forth" (towards lower'
        ' points first) and "Forth and back" (towards higher first) turn around at the ends and switch this value'
        ' at run time; "Loop" starts again at the first point; "Random" picks any other point with a free way (up'
        ' to five tries); "Go To End" stops at the last point.')),
    ('CPatrolPathAI', 'Ignore last point'): ('confirmed', '0x53c8d0, 0x53c7d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: one more point at the end of the path is skipped. The polygon's last stored point is never visited "
        'anyway.')),
    ('CPatrolPathAI', 'End of path action'): ('confirmed', '0x53c8d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run whenever the figure reaches an end of the path: turning around ("Back and forth"/"Forth and '
        'back"), starting a new round ("Loop") or stopping ("Go To End"); never with "Random". Empty: nothing.')),
    ('CPatrolPathAI', 'TimeBeforCanReviseData'): ('confirmed', '0x53c640', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds (0.5 after each new target) before a missed point may be aimed at again. '
        'Leave unchanged in a level.')),
    ('CPatrolPathAI', 'Revise Point'): ('confirmed', '0x53c640', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the path point to aim at again when the last move ended more than 10 pixels away '
        'from it. Leave unchanged in a level.')),
    ('CPatrolPathAI', 'Revising Data'): ('confirmed', '0x53c640, 0x53c5c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 while the figure is about to re-aim at "Revise Point". Leave unchanged in a '
        'level.')),
    ('CPatrolPathAI', 'Target Point'): ('confirmed', '0x53c7d0, 0x53c8d0, 0x53c640', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: index of the path point the figure is heading for (-1 = finished in "Go To End"); '
        'recomputed as the nearest point when the AI begins. Leave unchanged in a level.')),
    ('CPatrolPathAI', 'Moving'): ('confirmed', '0x53c8d0, 0x53c640', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move behaviour that walks the figure from point to point; its Play Ratio is the animation '
        'speed. The figure is set to walking (not running) when the AI begins.')),
    ('CScanAreaAI', 'Starting Angle'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'One end of the sweep, in degrees relative to the direction the figure faced when the scan began (-360 to'
        ' 360, default -45). The first sweep goes from that direction to "Ending Angle" (or to this angle with '
        '"Start Counterclockwise"), then the figure sweeps between both ends.')),
    ('CScanAreaAI', 'Ending Angle'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Other end of the sweep, in degrees relative to the starting facing (-360 to 360, default 45); the first '
        'sweep heads here unless "Start Counterclockwise" is set.')),
    ('CScanAreaAI', 'Turning Speed'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sweep speed in degrees per second (default 10); each sweep takes angle range / speed seconds and eases '
        'in and out. 0: the figure does not turn.')),
    ('CScanAreaAI', 'Time Between Turning'): ('confirmed', '0x565ce0, 0x565c10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds the figure pauses at each end of the sweep (default 0).')),
    ('CScanAreaAI', 'Start Out Waiting'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the scan begins with a pause of "Time Between Turning" before the first sweep (and the "End Turn '
        'Action" runs when that pause ends); 0 (default): it starts turning at once.')),
    ('CScanAreaAI', 'Start Counterclockwise'): ('confirmed', '0x565c10', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the first sweep goes towards "Starting Angle" instead of "Ending Angle".')),
    ('CScanAreaAI', 'Turn Sequence Name'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animation sequence (default "Idle") started at frame 0 when the scan begins and played on in a loop at '
        'its own speed the whole time, also during pauses.')),
    ('CScanAreaAI', 'End Turn Action'): ('confirmed', '0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when a pause at a sweep end is over: after every sweep with "Execute Each Turn", otherwise '
        'after every second sweep (once per full back-and-forth). Empty: nothing.')),
    ('CScanAreaAI', 'Execute Each Turn'): ('confirmed', '0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: "End Turn Action" runs after every sweep; 0 (default): only after every second sweep.')),
    ('CScanAreaAI', 'Reset Each Begin'): ('confirmed', '0x565c10', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 (default): every time the AI begins, the scan restarts from the figure's current facing. 0: only the "
        'first begin sets it up; later begins continue the old sweep around the original facing.')),
    ('CScanAreaAI', 'Current Time To Wait'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left in the current pause, set from "Time Between Turning". Leave '
        'unchanged in a level.')),
    ('CScanAreaAI', 'Current Start Angle'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the angle (degrees, relative to the starting facing) the current sweep starts '
        'from. Leave unchanged in a level.')),
    ('CScanAreaAI', 'Current End Angle'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the angle (degrees, relative to the starting facing) the current sweep heads for. '
        'Leave unchanged in a level.')),
    ('CScanAreaAI', 'Waiting'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 during a pause between sweeps; set from "Start Out Waiting" when the scan '
        'begins. Leave unchanged in a level.')),
    ('CScanAreaAI', 'Turning Flag'): ('confirmed', '0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: flips after every finished sweep; without "Execute Each Turn" the "End Turn '
        'Action" only runs while it is 0. Leave unchanged in a level.')),
    ('CScanAreaAI', 'Starting Facing Angle'): ('confirmed', '0x565c10, 0x565be0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the figure's facing (radians) when the scan was set up; all sweep angles are "
        'relative to it. -999 (default) means not yet taken, so the first begin always sets the scan up; leave at'
        ' -999 in a level.')),
    ('CScanAreaAI', 'Complete Turn Time'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: total seconds of the current sweep (angle range / "Turning Speed"). Leave '
        'unchanged in a level.')),
    ('CScanAreaAI', 'Current Turn Time'): ('confirmed', '0x565c10, 0x565ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left in the current sweep. Leave unchanged in a level.')),
    ('FollowAI', 'Leader Name'): ('confirmed', '0x4a55a0, 0x4a5790', QT_TRANSLATE_NOOP(
        'fieldhelp', "Name of the level object to follow, looked up in the figure's layer every time the AI begins. Without a "
        'match the follower stands still.')),
    ('FollowAI', 'Moving'): ('confirmed', '0x4a5790, 0x4a55a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded move behaviour aimed every frame at the spot beside the leader; its Play Ratio is the animation'
        ' speed.')),
    ('FollowAI', 'Turn'): ('confirmed', '0x4a5790', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded turn behaviour: once the follower has reached its spot it turns to face the same way as the '
        'leader.')),
    ('FollowAI', 'Current Leader'): ('confirmed', '0x4a55a0, 0x4a5890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the leader object found by "Leader Name"; cleared when the leader dies or is '
        'deleted, after which the follower stops. Leave unchanged in a level.')),
    ('FollowAI', 'Relative Position X'): ('confirmed', '0x4a55a0, 0x4a5790', QT_TRANSLATE_NOOP(
        'fieldhelp', "X of the follower's spot relative to the leader, in pixels in the leader's own turned frame (the spot "
        "turns with the leader). If X and Y are both 0 when the AI begins, the follower's current offset is "
        'taken; a value set in a level fixes the spot.')),
    ('FollowAI', 'Relative Position Y'): ('confirmed', '0x4a55a0, 0x4a5790', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y of the follower\'s spot relative to the leader, in the leader\'s turned frame; see "Relative Position X"'
        ' (both 0 = take the current offset at begin).')),
    ('CPercentInvulnerableAI', 'Damage To Take'): ('confirmed', '0x56dfe0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Share of incoming damage of the selected types the object actually takes, 0 to 1 (shown as %; default 1 '
        '= full damage, 0 = immune).')),
    ('CPercentInvulnerableAI', 'Damage Types'): ('confirmed', '0x56dfe0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage types that "Damage To Take" applies to (default all); damage of other types passes unchanged.')),
    ('CPlayerControlAI', 'Player Num'): ('confirmed', '0x542550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of the player whose input this control AI follows (default 0, the first player); setting it also '
        "fetches that player's object from the world.")),
    ('CPlayerWalkingControlAI', 'Played DryFire Sound'): ('confirmed', '0x543830', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set once the empty-weapon click has played, so it plays only once per trigger '
        'pull; cleared when firing stops. Leave unchanged in a level.')),
    ('CPointOfIntrestAI', 'Layer Part'): ('confirmed', '0x508b50, 0x508be0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the object this point-of-interest AI put into its layer's update monitor list when"
        ' it started. Leave unchanged in a level.')),
    ('CPointOfIntrestAI', 'Layer SaveData'): ('confirmed', '0x508b50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the save data of the layer whose update monitor list holds the object; set when '
        'the AI starts. Leave unchanged in a level.')),
    ('CPointOfIntrestAI', 'Already Added'): ('confirmed', '0x508b50, 0x508be0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: 1 while the object is in the layer's update monitor list; the AI takes it out "
        'again when it is deactivated. Leave unchanged in a level.')),
    ('CChasePursueAI', 'AFloat'): ('confirmed', '0x46cb10, 0x46cc40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The embedded move behaviour the pursuit uses to walk towards the target (its speed, path and move '
        'settings). About once per second it is re-aimed at the current target, or at the object itself when it '
        'has none; a move that finds no way sends a failed-target message so the owner gives up the target.')),
    ('CChasePursueAI', 'Play Ratio'): ('confirmed', '0x46cb10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Animation play ratio handed to each new move. It is overwritten with the move behaviour's speed whenever"
        ' that speed is above 0; if a move with it fails, the move is retried with 0.')),
    ('CChasePursueAI', 'Next Try To Move'): ('confirmed', '0x46cb10, 0x46caa0, 0x46cc40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until the move is re-aimed at the target (reset to 1 after each try, 0 at '
        'Begin and after a failed move). Leave unchanged in a level.')),
    ('CRelayAI', 'Action'): ('confirmed', '0x420290', QT_TRANSLATE_NOOP(
        'fieldhelp', "Action run when a CTriggerRelayAction names this object (the object must be active). The relay action's "
        'trigger and instigator are passed on to it.')),
    ('CRelayAI', 'Trigger Only Once'): ('confirmed', '0x420290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, the relay runs its "Action" only the first time; later relay calls are ignored.')),
    ('CRelayAI', 'Was Triggered'): ('confirmed', '0x420290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set when the relay has run its action. Together with "Trigger Only Once" a 1 here '
        'blocks the relay from the start.')),
    ('CRepeatTimerTriggerAI', 'Action'): ('confirmed', '0x4208c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run again and again on a timer (trigger and instigator: the object holding the timer).')),
    ('CRepeatTimerTriggerAI', 'Delay Between Actions'): ('confirmed', '0x4208c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Average time in seconds between two runs of "Action" (at least 1/60 s; default 1).')),
    ('CRepeatTimerTriggerAI', 'Plus or Minus'): ('confirmed', '0x420880, 0x4208c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Random variation in seconds: each interval is picked at random between "Delay Between Actions" minus and'
        ' plus this value (never below 1/60 s). Above 0 it also makes the first run come after a random time '
        'between 0 and delay plus this value; at 0 the first run happens on the first update.')),
    ('CRepeatTimerTriggerAI', 'Seconds Till Next Execute'): ('confirmed', '0x420880, 0x4208c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left until the next run of "Action". It is recomputed when the timer '
        'starts, so a level value has no lasting effect; leave unchanged.')),
    ('CSameAsParentAI', 'Force Invisable'): ('confirmed', '0x562010, 0x5453c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "For an upper-body part that copies its parent's animation: when set, the part stays hidden while still "
        "following the parent's sequence and frame. In CPlayerWalkingItemAI and CPlayerWalkingWeaponAI the game "
        'sets this value itself every frame.')),
    ('CSameAsParentAI', 'Only Show First Sequence'): ('confirmed', '0x562010', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, the part always plays its own first sequence (only the frame follows the parent) instead of '
        "the parent's sequence of the same name. When unset and the part lacks the parent's current sequence, it "
        'is hidden.')),
    ('CPlayerWalkingItemAI', 'Type Index'): ('confirmed', '0x5453c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Inventory category of the item this part shows (e.g. the hand-held item). The part is visible only while'
        ' the character\'s current item of this category exists and is of "Definition Index".')),
    ('CPlayerWalkingItemAI', 'Definition Index'): ('confirmed', '0x5453c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Item definition (catalogue entry) the character\'s current item of "Type Index" must have for this part '
        'to be shown; otherwise it is hidden.')),
    ('CWalkingUpperBodyAI', 'Extra Hold Delay'): ('confirmed', '0x595ff0, 0x596160', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds the upper body keeps its shooting pose after the discharge sequence before it follows the legs '
        'again. Every shot sets it to 0.2, so it is mostly run-time state; a level value only delays the first '
        'follow.')),
    ('CWalkingUpperBodyAI', 'Last Discharge Sequence'): ('confirmed', '0x595ff0, 0x596160', QT_TRANSLATE_NOOP(
        'fieldhelp', "Name of the upper body's shooting sequence; while it plays, the character counts as still shooting until"
        ' its last frame. Every shot overwrites it with the weapon\'s discharge sequence (or "Shoot1"), so it is '
        'mostly run-time state.')),
    ('CSelectiveCollideAI', 'Collides with'): ('confirmed', '0x56ab30, 0x4fbe60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Categories this object still collides with; objects of all other categories pass through it. Empty means'
        ' nothing is blocked.')),
    ('CSeriesAI', 'AIs'): ('confirmed', '0x56cd50, 0x56cc40, 0x56ccf0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The AIs run one after another. Only the current one gets updates and messages; the series moves on when '
        'the current AI reports "AI done" (e.g. through a CSendAIDoneMessage), telling the old one to deactivate '
        'and beginning the next.')),
    ('CSeriesAI', 'Current AI'): ('confirmed', '0x56ccb0, 0x56cd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: index of the AI the series is at (0 = first). Begin resumes at this index unless '
        'the series is past its end or "Restart Series Next Begin" is set, so a level value starts the series at '
        'that entry.')),
    ('CSeriesAI', 'When Done'): ('confirmed', '0x56cd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'What happens after the last AI: "Repeat Series" starts again with the first AI; "Do Nothing" (default) '
        'tells the object that this AI is done (so an enclosing series or temporary task can continue) and the '
        'series stays finished.')),
    ('CSeriesAI', 'Restart Series Next Begin'): ('confirmed', '0x56ccb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, every Begin of the series starts again with the first AI; otherwise it resumes with the AI it '
        'was at.')),
    ('CShieldAI', 'ShieldEntity'): ('confirmed', '0x56d960, 0x56dc50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the shield graphic object, created as a child of the character on the first hit '
        'from the shield item\'s "Shield Gfx" and forgotten when it dies or is deleted. Leave unchanged in a '
        'level.')),
    ('CShieldAI', 'Damage Type'): ('confirmed', '0x56da70, 0x56d7d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Damage type this shield blocks. It looks for the character's shield item of the same type; while that "
        'item has charge, damage of the type is absorbed completely and drained from the charge (more damage than'
        ' charge left shuts the shield down). Other damage types pass unchanged.')),
    ('CSimultaneousAIsAI', 'AIs'): ('confirmed', '0x4cba30, 0x4cba60, 0x4cb9e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AIs that all run at the same time: each gets Begin, updates, collisions and messages in list order; a '
        'message counts as handled when any of them handles it.')),
    ('CSkeletonAI', 'Patrol AI'): ('confirmed', '0x5776d0, 0x576730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI the character runs while patrolling (the state at start and after losing a target); default '
        'CPatrolAreaAI. While patrolling the character also looks for targets.')),
    ('CSkeletonAI', 'Patrol Start Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character enters the patrol state (trigger and instigator: the character).')),
    ('CSkeletonAI', 'Patrol End Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character leaves the patrol state.')),
    ('CSkeletonAI', 'Target shooter if hit'): ('confirmed', '0x5762e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, a patrolling character without a target makes whoever damaged it its target and goes to attack'
        ' or pursue.')),
    ('CSkeletonAI', 'Never Unacquire'): ('confirmed', '0x576730, 0x5762e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, the character keeps its target: it ignores failed-target messages, does not give up the '
        'pursuit for being too far from home, does not search for a new target while investigating, and '
        'investigates instead of patrolling when the target is gone during an attack.')),
    ('CSkeletonAI', 'Target Type'): ('confirmed', '0x576c50, 0x576730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded target search: the sight radius in pixels, the categories the character targets and its angle '
        'of view. While patrolling it picks the closest visible object of these categories within the radius '
        '(vertical distances count about 1.4 times).')),
    ('CSkeletonAI', 'Has Seen Target'): ('confirmed', '0x5779a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: set the first time the character acquires a target, which also plays its model's "
        'alert sound once. A 1 in a level suppresses that first sound.')),
    ('CSkeletonAI', 'Max dist from home'): ('confirmed', '0x576f80, 0x576730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Distance in pixels from its home position the character may pursue (default 500). Beyond it the pursuit '
        'is given up (back to patrol, "Target Lost"), unless "Never Unacquire" is set; targets further than this '
        'plus "Max Dist" from home are not picked up.')),
    ('CSkeletonAI', 'Pursue AI'): ('confirmed', '0x5776d0, 0x576730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI the character runs while pursuing a visible target that is further away than "Max Dist".')),
    ('CSkeletonAI', 'Pursue Start Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character enters the pursue state.')),
    ('CSkeletonAI', 'Pursue End Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character leaves the pursue state.')),
    ('CSkeletonAI', 'Max distance from home'): ('confirmed', '0x575330', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect: the game\'s code never reads this value; only "Pursue/Max dist from home" limits the '
        'character.')),
    ('CSkeletonAI', 'Investigate End Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character leaves the investigate state.')),
    ('CSkeletonAI', 'Investigate Start Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character enters the investigate state.')),
    ('CSkeletonAI', 'Investigate AI'): ('confirmed', '0x5776d0, 0x576730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI the character runs while investigating: when it loses sight of its target during pursuit or attack. '
        'Default CChaseInvestigateAI; seeing the target within its view angle switches back to pursuit.')),
    ('CSkeletonAI', 'Max Dist'): ('confirmed', '0x576730, 0x5779a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Attack range in pixels (default 200; vertical distances count about 1.4 times): within it the character '
        'attacks, beyond it it pursues.')),
    ('CSkeletonAI', 'Attack AI'): ('confirmed', '0x5776d0, 0x576730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI the character runs while attacking a visible target within "Max Dist"; default CNormalAttackAI.')),
    ('CSkeletonAI', 'Attack Start Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character enters the attack state.')),
    ('CSkeletonAI', 'Attack End Action'): ('confirmed', '0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run each time the character leaves the attack state.')),
    ('CSkeletonAI', 'Retreat when'): ('confirmed', '0x5762e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Health in percent (0–100, default 40) at or below which a hit runs "Retreat Start Action" once. The '
        'character does not change its state by itself; the action has to make it retreat.')),
    ('CSkeletonAI', 'Retreat Start Action'): ('confirmed', '0x5762e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run once when a hit leaves the character at or below "Retreat when" percent health.')),
    ('CSkeletonAI', 'Has Started Retreat'): ('confirmed', '0x5762e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set when the retreat action has run. A 1 in a level prevents "Retreat Start '
        'Action" from ever running.')),
    ('CSkeletonAI', 'State'): ('confirmed', '0x5776d0, 0x576200', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the current state (Patrol, Pursue, Attack, Retreat, Investigate). Begin always '
        'sets it to Patrol; leave unchanged in a level.')),
    ('CSkeletonAI', 'Transition'): ('confirmed', '0x577a90, 0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'List of state transitions: each entry runs its action when the character changes from "From State" to '
        '"To State" ("Any" matches all; "Target Acquired" and "Target Lost" are extra events). "Trigger" decides '
        'whether it runs only the first time, every time, or once per new target.')),
    ('CSpawnPointAI', 'Spawn Action'): ('confirmed', '0x420d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when an object is spawned at this spawn point (trigger: the spawn point, instigator: the '
        'spawned object), after its facing has been set.')),
    ('CSpawnPointAI', 'Set Facing Angle'): ('confirmed', '0x420d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, an animated object spawned here is turned to "Facing Angle"; for the player character the '
        'movement controls take over that direction too.')),
    ('CSpawnPointAI', 'Facing Angle'): ('confirmed', '0x420d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Direction in degrees (0–360, default 180) a spawned object faces when "Set Facing Angle" is set.')),
    ('CTemporaryTaskAI', 'Temporary AI'): ('confirmed', '0x58b2a0, 0x58b380, 0x58b410', QT_TRANSLATE_NOOP(
        'fieldhelp', "AI that temporarily replaces the object's first AI and gets all its updates, collisions and messages. "
        'When it reports "AI done", the original AI is put back. Must not be empty (the game does not check it).')),
    ('CTemporaryTaskAI', 'Original AI'): ('confirmed', '0x58b2a0, 0x58b380', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the object's original AI, kept aside while the temporary AI runs and restored "
        'afterwards. Leave unchanged in a level.')),
    ('CTemporaryTaskAI', 'Supress Begin After Done'): ('confirmed', '0x58b380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, the restored original AI is not restarted (no Begin) after the temporary AI is done; it simply'
        ' continues.')),
    ('CTriggerAI', 'Trigger Only Once'): ('confirmed', '0x422cd0, 0x422510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, the trigger fires its action only once; afterwards it stays inactive (a touching trigger stops'
        ' checking altogether).')),
    ('CTriggerAI', 'Was Triggered'): ('confirmed', '0x422cd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set when the trigger has fired. Together with "Trigger Only Once" a 1 here '
        'disables the trigger from the start.')),
    ('CTriggerAI', 'Auto-Flip Switch'): ('confirmed', '0x422cd0, 0x4bce40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only matters when the trigger\'s own object is a switch (its model has a "Switch" or "Switching" '
        'sequence): then the trigger fires only while the switch stands in "Idle" or "Switched", and flips it '
        'after firing. Default 1.')),
    ('CTriggerAI', 'Trigge Must Have HP'): ('confirmed', '0x422d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, a destructible object with no hit points left (e.g. a dead character) cannot set off the '
        'trigger, unless it matches "Triggered By Name".')),
    ('CTriggerAI', 'Triggered By Anything'): ('confirmed', '0x422d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, any object can set off the trigger (subject to "Trigge Must Have HP").')),
    ('CTriggerAI', 'Triggered By Players'): ('confirmed', '0x422d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, objects of the player category can set off the trigger. Default 1.')),
    ('CTriggerAI', 'Triggered By Enemies'): ('confirmed', '0x422d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, objects of the enemy category can set off the trigger.')),
    ('CTriggerAI', 'Triggered By Projectiles'): ('confirmed', '0x422d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, projectiles (objects with a shot AI) can set off the trigger.')),
    ('CTriggerAI', 'Triggered By Name'): ('confirmed', '0x422d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of an object that can always set off the trigger (case ignored), regardless of the other "Triggered'
        ' By" settings and the hit point check. Empty: no name check.')),
    ('CPassThroughTriggerAI', 'Action'): ('confirmed', '0x41d3b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Action run on every collision with an object the trigger allows (trigger: the trigger's object, "
        'instigator: the colliding object); there is no retrigger delay.')),
    ('CTouchingTriggerAI', 'Enter Action'): ('confirmed', '0x422510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when an allowed object starts touching the trigger area (instigator: that object). Not run '
        'for an animated object within its first 4 updates after being placed or teleported.')),
    ('CTouchingTriggerAI', 'Exit Action'): ('confirmed', '0x422510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when no allowed object touches the trigger area any more (instigator: the object that touched'
        ' it last).')),
    ('CTouchingTriggerAI', 'Repeat Action'): ('confirmed', '0x422510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run repeatedly every "Repeat Every" seconds while an object touches the trigger area; the first '
        'run comes right on entering.')),
    ('CTouchingTriggerAI', 'Repeat Every'): ('confirmed', '0x422510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Interval in seconds for "Repeat Action" while touching; 0 (default) switches the repeat off.')),
    ('CTouchingTriggerAI', 'Touching LayerPart'): ('confirmed', '0x422510, 0x4226f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the object currently touching the trigger area. Leave unchanged in a level.')),
    ('CTouchingTriggerAI', 'Next Repeat Time'): ('confirmed', '0x422510', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the game time in seconds at which "Repeat Action" runs next. Leave unchanged in a '
        'level.')),
    ('CTouchingOvalTriggerAI', 'X Radius'): ('confirmed', '0x421320, 0x421390', QT_TRANSLATE_NOOP(
        'fieldhelp', "Horizontal radius in pixels of the oval trigger area around the object's centre (default 30).")),
    ('CTouchingOvalTriggerAI', 'YX Ratio'): ('confirmed', '0x421390, 0x421410', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height-to-width ratio of the oval: the vertical radius is "X Radius" times this value (default about '
        "0.713, the game's ground perspective).")),
    ('CollideTriggerAI', 'Action'): ('confirmed', '0x41cf10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Action run when an allowed object collides with the trigger's object, unless the collision falls within "
        'the retrigger lock (then "Action for Failed Retrigger" runs instead).')),
    ('CollideTriggerAI', 'Disallow Retrigger'): ('confirmed', '0x41cf10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Lock time in seconds after a successful trigger (default 0.5): collisions within it run "Action for '
        'Failed Retrigger" instead of "Action". 0 switches the lock off.')),
    ('CollideTriggerAI', 'Last Trigger Time'): ('confirmed', '0x41cf10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the game time in seconds of the last successful trigger, used for the retrigger '
        'lock. Leave at 0 in a level.')),
    ('CollideTriggerAI', 'Retrigger Disallow Time For'): ('confirmed', '0x41cbf0, 0x41cf10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect: the game never reads this choice. The retrigger lock always uses one shared time for all '
        'objects, as "All Objects" (default) suggests; "Each Object" behaves the same.')),
    ('CollideTriggerAI', 'Action for Failed Retrigger'): ('confirmed', '0x41cf10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run instead of "Action" when an allowed object collides while the retrigger lock ("Disallow '
        'Retrigger") is still running.')),
    ('CTurretAI', 'Start Attack'): ('confirmed', '0x58deb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Attack radius in pixels (1–640, default 200): the turret targets the nearest active object of "Valid '
        'Targets" within it that it has a free line of fire to (vertical distances count about 1.4 times). Works '
        'only on character objects.')),
    ('CTurretAI', 'Stop Attack Extra'): ('confirmed', '0x58deb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels added to "Start Attack" while the turret has a target in sight (default 40), so a target must '
        'move this much further away before the turret stops.')),
    ('CTurretAI', 'Num Shots In Burst'): ('confirmed', '0x58deb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of shots per burst (1–5, default 3), 0.2 seconds apart, each turning towards the target.')),
    ('CTurretAI', 'Burst Delay'): ('confirmed', '0x58deb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pause in seconds before each burst (0–20, default 2).')),
    ('CTurretAI', 'Valid Targets'): ('confirmed', '0x58deb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Categories the turret attacks (default Player).')),
    ('CTurretAI', 'Deploy Angle'): ('confirmed', '0x58de70, 0x58deb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Facing in degrees (0–360) the turret takes at start and when it deploys or folds back; it unfolds with '
        '"Deploy" into "Shoot1" to attack and plays "Deploy" backwards into "Idle" without a target.')),
    ('CTurretAI', 'Retry Time'): ('confirmed', '0x58deb0, 0x58daa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds until the turret looks for a target again (every 0.3 s). The editor shows '
        '"Degrees" as its unit, a mistake of the original. A level value only delays the first check.')),
    ('CAutoGunAI', 'PickupDelay'): ('confirmed', '0x58eff0, 0x58f010', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds (default 3) before the player can pick the auto gun up; the value counts down while the gun '
        'runs, so in a save game it is the time left.')),
    ('CAutoGunAI', 'PickupAI'): ('confirmed', '0x58f010, 0x58f0b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Embedded pickup AI that handles picking up the auto gun by objects of the player category once '
        '"PickupDelay" is over.')),
    ('CWaitAI', 'Time To Wait'): ('confirmed', '0x4cc3b0, 0x4cc400', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Wait time in seconds (default 1); "Done Action" runs once when it has passed.')),
    ('CWaitAI', 'Time Left'): ('confirmed', '0x4cc3b0, 0x4cc400', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left of the wait; Begin sets it to "Time To Wait". Leave unchanged in a '
        'level.')),
    ('CWaitAI', 'Done Action'): ('confirmed', '0x4cc400', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run once when the wait is over (trigger and instigator: the object). Default: a '
        'CSendAIDoneMessage, which lets an enclosing series continue.')),
    ('CWaitAI', 'Behavior to run'): ('confirmed', '0x4cc3b0, 0x4cc400', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Entity behaviour (e.g. an animation) the object performs during the wait; it starts at Begin and gets '
        'every update. It only acts on animated objects.')),
    ('CWhileAI', 'Condition to test'): ('confirmed', '0x4cbeb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action tested on every update; while it succeeds, "What to do while waiting" runs. Empty counts as '
        'always true.')),
    ('CWhileAI', 'What to do while waiting'): ('confirmed', '0x4cbeb0, 0x4cbe90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI that runs while the condition holds; it gets Begin, collisions, messages and the updates of the '
        'frames in which the condition succeeds.')),
    ('CWhileAI', 'Done Action'): ('confirmed', '0x4cbeb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the condition fails; it runs again on every update for as long as the condition keeps '
        'failing. Default: a CSendAIDoneMessage.')),
    ('CActivateAction', 'Target Name'): ('confirmed', '0x4c29c0, 0x4c29f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects to activate (names, comma lists, "$Trigger", "$Instigator" and the like). Only inactive objects '
        'are affected.')),
    ('CActivateAction', 'Play Activate Sound'): ('confirmed', '0x4c29f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "When set, each activated object plays its model's activation sound.")),
    ('CActivateAction', 'Delay Between Activations'): ('confirmed', '0x4c29c0, 0x41aed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds between activating one target and the next when the name matches several objects (0 = all at '
        'once). The first is activated at once, the others are queued.')),
    ('CActivateAction', 'Warp Behavior'): ('confirmed', '0x4c29f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Optional behaviour (e.g. a warp-in effect) an activated animated object performs first; it runs as a '
        "temporary task, after which the object's own AI continues.")),
    ('CAddAIAction', 'Target Name'): ('confirmed', '0x4c29c0, 0x4c4690', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects that get the AI (names, comma lists, "$Trigger", "$Instigator" and the like).')),
    ('CAddAIAction', 'AI'): ('confirmed', '0x4c4690', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI template; each target gets its own copy added to its AIs.')),
    ('CAddAIAction', 'Delay Between Adds'): ('confirmed', '0x4c29c0, 0x41aed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds between adding the AI to one target and the next when the name matches several objects (0 = all '
        'at once).')),
    ('CAddEffectAction', 'Who To Warp'): ('confirmed', '0x4c7ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects that get the effect (default "$Instigator"); only animated objects are affected.')),
    ('CAddEffectAction', 'Warp Sound'): ('confirmed', '0x4c7ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played at each affected object; empty for none.')),
    ('CAddEffectAction', 'Warp Behavior'): ('confirmed', '0x4c7ce0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Behaviour template; each affected object gets a copy pushed onto its behaviour stack with priority 2 '
        '(e.g. a warp effect).')),
    ('CAddMissionObjective', 'New Objective'): ('confirmed', '0x513780, 0x512170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objective added (as a copy) to the current mission. It is refused when its ID tag is already used; '
        'without a mission only a warning is given.')),
    ('CAssignTemporaryTaskAction', 'Target'): ('confirmed', '0x4c3020, 0x58b770', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects that get the temporary task (names, comma lists, "$Trigger", "$Instigator" and the like).')),
    ('CAssignTemporaryTaskAction', 'Temporary Task AI'): ('confirmed', '0x58b770, 0x58b2a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AI template; each target gets a copy that replaces its first AI until the copy reports "AI done", then '
        'the original AI is restored and restarted.')),
    ('CBeginNonInteractiveSequenceAction', 'Camera Speed'): ('confirmed', '0x522110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In pixels per second (default 30).')),
    ('CBeginNonInteractiveSequenceAction', 'Current Scene Index'): ('confirmed', '0x521e90, 0x522110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the index of the scene being played (0 = first); reset when the sequence starts. '
        'Leave unchanged in a level.')),
    ('CBeginNonInteractiveSequenceAction', 'State'): ('confirmed', '0x521e90, 0x522110, 0x5222a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: where the sequence is (not playing, camera moving to a scene, in a scene, camera '
        'returning, returned); reset when the sequence starts. Leave unchanged in a level.')),
    ('CBroadcastMessageToAreaAction', 'Message'): ('confirmed', '0x4c6aa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the message sent to the objects in the area; empty sends nothing.')),
    ('CBroadcastMessageToAreaAction', 'Position'): ('confirmed', '0x4c6a70, 0x4c6aa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'If the name matches several objects, each of them gets its own area; only active objects receive the '
        'message.')),
    ('CCallForReinforcementsAction', 'Requester Name'): ('confirmed', '0x5743c0, 0x4c3020', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Object(s) the call is about (default "$Trigger"). Original quirk: the call is always made by the object '
        'that triggered the action and against its current target; the name only has to match, and each match '
        'repeats the call. Without a target nobody answers.')),
    ('CCallForReinforcementsAction', 'Max Distance'): ('confirmed', '0x5743c0, 0x55d070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Radius in pixels (default 500) of the oval around the caller; active objects in it that share a category'
        ' with the caller get the call, and characters with "Respond to calls for reinforcements" may take on the'
        " caller's target.")),
    ('CChangeSoundEnvironmentTypeAction', 'Environment Type'): ('confirmed', '0x4c5730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect: the action hands the type to a sound function that does nothing in this version of the game.')),
    ('CCheckCurSequenceAction', 'Target Name'): ('confirmed', '0x4c42a0, 0x4bf5f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animated objects whose current sequence is checked (names, comma lists, "$Trigger" and the like); other '
        'objects are reported as wrong class. The check succeeds when any of them plays "Animation".')),
    ('CCheckCurSequenceAction', 'Animation'): ('confirmed', '0x4bf5f0, 0x587d30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence name to compare with; case, leading and trailing spaces and repeated spaces are ignored. Empty '
        'always fails.')),
    ('CCheckExistenceAction', 'Name To Check For'): ('confirmed', '0x4c5db0, 0x4c5a70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects to count (names, comma lists, "$Trigger" and the like); only active objects count.')),
    ('CCheckExistenceAction', 'Desired Minimum Count'): ('confirmed', '0x4c5db0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The check succeeds when at least this many active objects match (default 1).')),
    ('CCheckForInventoryItemBaseAction', 'Inventory Item Definition'): ('confirmed', '0x5b30f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Item definition (catalogue entry) looked for in the inventory of the action's instigator, which must be "
        'an object with hit points.')),
    ('CCheckForInventoryItemBaseAction', 'Count'): ('confirmed', '0x5b30f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How many items of the definition are needed (default 1); CUseInventoryItemAction also uses up this many '
        'on success.')),
    ('CCheckForInventoryItemBaseAction', 'Legacy Succeed Action Do NOT use'): ('confirmed', '0x5b30f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Old field (formerly "Succeed Action"), still run when the check succeeds; use the result of the action '
        '(e.g. in a conditional action) instead. Hidden in CUseInventoryItemAction.')),
    ('CCheckForInventoryItemBaseAction', 'Legacy Fail Action Do NOT use'): ('confirmed', '0x5b30f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Old field (formerly "Fail Action"), still run when the instigator lacks the items; use the result of the'
        ' action instead. Hidden in CUseInventoryItemAction.')),
    ('CConditionalAction', 'Try Action'): ('confirmed', '0x41bba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The condition: this action runs first; its result decides whether the second or the third action runs. '
        'Without it the whole action does nothing and fails.')),
    ('CConditionalAction', 'Succeed Action'): ('confirmed', '0x41bba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Runs when "Try Action" succeeded; its result becomes the result of the whole action. Empty: the action '
        'simply succeeds.')),
    ('CConditionalAction', 'Fail Action'): ('confirmed', '0x41bba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Runs when "Try Action" failed. The whole action then always counts as failed, whatever this action '
        'returns.')),
    ('CCopyColorAction', 'Entity To Change'): ('confirmed', '0x5a95b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the object that receives the colour (hue remap). Names, comma lists, "$Trigger" and '
        '"$Instigator" work; it must resolve to exactly one object, otherwise nothing happens (no warning is '
        'printed).')),
    ('CCopyColorAction', 'Entity To Copy Color From'): ('confirmed', '0x5a95b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the object whose colour (hue remap) is copied; default "$Instigator". It must resolve to exactly'
        ' one object that has a colour of its own, otherwise nothing happens. If the receiver already has a '
        'colour only its two hue values are copied; if it has none it gets a full copy, but the action then '
        'reports failure.')),
    ('CCopyColorAction', 'Copy From First Child'): ('confirmed', '0x5a95b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'If the source object has no children, the object itself is used.')),
    ('CCreateLayerPartAction', 'New Location'): ('confirmed', '0x4bc160, 0x4bc1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Accepts names, comma lists, "$Trigger"/"$Instigator"; the new object is put into the layer of that '
        'location object. Default "$Trigger" (CCloneAction: empty).')),
    ('CCreateLayerPartAction', 'Random Location Delta'): ('confirmed', '0x4bc230', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Scatter radius in pixels: when above 0, the new object is moved a random distance between 0 and this '
        'value in a random direction from its location (or from its own position when no location is given). 0 = '
        'no scattering.')),
    ('CCreateLayerPartAction', 'Warp Behavior'): ('confirmed', '0x4bc230, 0x4bc0f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Optional entity behaviour (usually CEntityBehaviorWarpEffect) that the new object plays as its '
        'appearance effect. If the created object is a plain entity that cannot animate, it is replaced by an '
        'animated copy so the effect can play. Old files with "Warp In" = non-zero get a warp behaviour here '
        'automatically.')),
    ('CCloneAction', 'Source Name'): ('confirmed', '0x4bbcc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the object to copy (names, "$Trigger", "$Instigator" work). It must resolve to exactly one '
        'object; otherwise a warning is printed and nothing is created. Without a "New Location" the copy appears'
        ' where the source is.')),
    ('CCloneAction', 'New Name'): ('confirmed', '0x4bbcc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name given to the copy, so later actions can address it. Empty: the copy has no name.')),
    ('CCloneAction', 'Set Facing Angle'): ('confirmed', '0x4bbcc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked, an animated copy is turned to "New Facing Angle"; otherwise it keeps the source\'s '
        'direction. Ignored for objects that are not animated entities.')),
    ('CCloneAction', 'New Facing Angle'): ('confirmed', '0x4bbcc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Direction the copy faces when "Set Facing Angle" is checked, in radians (0 to 2π; the editor shows '
        'degrees).')),
    ('CCreateCustomEntityAction', 'Entity'): ('confirmed', '0x4bcd30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The complete entity, configured here in place, of which a copy is created each time the action runs. '
        'Empty: nothing is created.')),
    ('CCreateDefaultEntityAction', 'Model to Create'): ('confirmed', '0x4bc910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model whose default entity is created (at least a CEntityBase), e.g. "Items/Money/Ore deposit 1".')),
    ('CCreateDefaultEntityAction', 'New Name'): ('confirmed', '0x4bc910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name given to the created entity, so later actions can address it. Empty: no name.')),
    ('CDeactivateAction', 'Target Name'): ('confirmed', '0x4c3020, 0x4c2d60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects to deactivate (names, comma lists, ranges like "a#1-5#", "$Trigger", "$Instigator", '
        '"$Touching"). An inactive object is not drawn, does not collide and does nothing until activated again. '
        'Succeeds if at least one object was active.')),
    ('CDefineMission', 'Mission'): ('confirmed', '0x512d20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The mission (CMission with its objectives) that becomes the current one. In the single-player quest game'
        ' the previous mission is finished first; a copy is added unless its ID tag is already used (then a '
        'warning, the old mission stays current). The mission timer restarts.')),
    ('CDefineMission', 'List of maps not to flush'): ('confirmed', '0x512d20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Map names (as cached, e.g. "ACT 2/M8/08 Pits Holding") whose saved state is kept in memory when the '
        'mission starts. Every other cached map except the current one is flushed (its state is written out and '
        'removed from the cache) unless it is already expired.')),
    ('CDelayAction', 'Next Action'): ('confirmed', '0x4b6950, 0x41c700', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action to run later. A copy of it is queued in the layer each time this action runs, so it can be '
        'pending several times at once. The delay action itself always succeeds immediately.')),
    ('CDelayAction', 'Delay'): ('confirmed', '0x4b6950, 0x41c700', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Waiting time in seconds of game time before "Next Action" runs (default 1).')),
    ('CDelayAction', 'Plus or Minus'): ('confirmed', '0x4b6950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Random variation in seconds: the actual delay is chosen at random between "Delay" minus and plus this '
        'value (never below 0). 0 = always exactly "Delay".')),
    ('CDelayAction', 'Forget Trigger'): ('confirmed', '0x4b6950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked, the delayed action runs without the trigger ("$Trigger" and the triggering AI are empty '
        'then); only the instigator is passed on. Useful when the trigger may be gone by then.')),
    ('CDeleteAction', 'Target Name'): ('confirmed', '0x4c3020, 0x4c3050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects that are removed from the level at once (names, comma lists, ranges, "$Trigger", "$Instigator", '
        '"$Touching"), without damage or death effects. Succeeds if at least one object was found.')),
    ('CDeleteMissionObjective', 'Objective Id Tag'): ('confirmed', '0x514310', QT_TRANSLATE_NOOP(
        'fieldhelp', 'ID tag of the objective that is removed from the current mission (compared without regard to case). '
        'Without a current mission or a matching objective a warning is printed and the action fails.')),
    ('CDestroyAction', 'Target'): ('confirmed', '0x4c3f80, 0x4c3fb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects to kill: every destructable entity the name resolves to takes all its remaining hit points as '
        '"Unavoidable" damage from the instigator, so it dies with its normal death effects. Objects without hit '
        'points cause a warning.')),
    ('CDialogActionBase', 'Script'): ('confirmed', '0x5a4bd0, 0x5a4f40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Dialogue script (an .RDS file of the mission, e.g. "ACT 1/M7/Mission07") that contains the line to say.')),
    ('CDialogActionBase', 'Line'): ('confirmed', '0x5a4bd0, 0x5a4c90, 0x5a4f40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The line of the script to show. A text "Speaker: text" is split into speaker and text (speaker up to 19 '
        'characters); the voice file "<line name>.wav" plays when voice-overs are on.')),
    ('CZaxDialogAction', 'Display Type'): ('confirmed', '0x5a4a90, 0x5a4f40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the line is shown: "Window with pause" opens the dialogue window with the speaker\'s portrait and '
        'pauses the game; "Scroll no pause" shows the text as a HUD message; "Center Fade No Pause" shows it as '
        'status text in the middle of the screen for 1.5 s.')),
    ('CZaxDialogAction', 'Say To'): ('confirmed', '0x5a4f40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Multiplayer only, for the two no-pause display types: "One Player" sends the line only to the player of '
        'the instigator, "All Players" to everyone. Ignored in single player.')),
    ('CZaxDialogAction', 'Execute After Action'): ('confirmed', '0x5a4a90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'While a cut-scene is being skipped it runs at once.')),
    ('CDiscoverInventoryItemAction', 'Inventory Item Definition'): ('confirmed', '0x5a6390', QT_TRANSLATE_NOOP(
        'fieldhelp', "Item type that becomes discovered (known) in the player's inventory. It always affects the first player "
        'character, not the trigger. The item definition must have "Must Be Discovered First" set, otherwise a '
        'warning is printed and the action fails.')),
    ('CDiscoverInventoryItemAction', 'Disable'): ('confirmed', '0x5a6390', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked, the item type is made undiscovered again instead of discovered.')),
    ('CDisplayMissionCompletedScreenAction', 'Completed Message'): ('confirmed', '0x515300', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text (translatable via Local.txt) shown in the mission-over window that this action opens, together with'
        " the current mission's statistics.")),
    ('CDisplayMissionFailedScreenAction', 'Failed Message'): ('confirmed', '0x515000', QT_TRANSLATE_NOOP(
        'fieldhelp', "Text (translatable via Local.txt) handed to the game type's mission-failed handling, which shows it in "
        'the mission-over window; the default is a placeholder meant to be replaced.')),
    ('CDropAllOreAndCrystalsAction', 'OreAndCrystalsPileModel'): ('confirmed', '0x5a6e50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model of the pile in which the trigger character drops all its ore and crystals (default '
        '"Ore_Crystals01"). The pile is placed near the character (within 500 pixels). Only works when the '
        'trigger is a character carrying ore or crystals; the action always reports failure.')),
    ('CDropAllOreAndCrystalsAction', 'Extra Pickup Action'): ('confirmed', '0x5a6e50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Optional action that runs additionally when the pile is picked up (touched); the pile then gives back '
        'the ore and crystals and removes itself.')),
    ('CDropCurrentItemOfTypeAction', 'Drop Item Action'): ('confirmed', '0x5a75c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The built-in drop action (no settings of its own) that drops the selected item as a pickup. It is run '
        "with the trigger character's inventory pointed at the current item of the chosen category; afterwards "
        'the inventory selection is restored.')),
    ('CDropCurrentItemOfTypeAction', 'Inventory Item Type To Drop'): ('confirmed', '0x5a75c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Item category (e.g. "Primary", the default) whose currently selected item the trigger character drops. '
        'Only works when the trigger is a character with an inventory.')),
    ('CExpireMapAction', 'Other Map Name'): ('confirmed', '0x58a690', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Map (path below "Levels/" without ".zax", e.g. "ACT 1/M7/07 Village Main") whose saved state is expired:'
        ' it should not be visited again (loading it afterwards shows the "Expired Error" level), and pending '
        'other-map actions for it are dropped. Not possible for the map currently shown; unknown maps cause a '
        'warning and failure.')),
    ('CExpireMapsInFolderAction', 'Map Directory'): ('confirmed', '0x58aaa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Folder below "Levels/" (e.g. "ACT 1/M6"; trailing slashes are ignored) whose maps (*.zax) are all '
        'expired as by CExpireMapAction. Empty is refused with a warning; a folder without maps causes a warning '
        'and failure.')),
    ('CFailAction', 'Action'): ('confirmed', '0x4bb270', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action that is run; whatever it returns, this action always reports failure. Empty: just fails.')),
    ('CFakeRenderHeightAction', 'Target'): ('confirmed', '0x4c6e30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Entities whose drawing height is changed (names, comma lists, "$Trigger" etc.); objects that are not '
        'entities are skipped.')),
    ('CFakeRenderHeightAction', 'New Render Height'): ('confirmed', '0x4c6e30', QT_TRANSLATE_NOOP(
        'fieldhelp', "New height above the ground in pixels. The entity's ground position is moved by the difference at the "
        'same time, so it stays where it is drawn on screen; only its sorting and shadow position change.')),
    ('CFlipSwitchAction', 'Switch Name'): ('confirmed', '0x4c42a0, 0x4bce40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Switches to flip (animated entities). A switch standing in "Idle" plays "Switching" (or "Switch") '
        'forwards and ends in "Switched"; one in "Switched" plays it backwards and ends in "Idle". Switches in '
        'any other sequence, or whose model lacks these sequences, are left alone.')),
    ('CFlushMapAction', 'Other Map Name'): ('confirmed', '0x58a2f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Map (path below "Levels/" without ".zax") whose cached state is flushed: written out and removed from '
        'memory; it keeps its state and is reloaded from it on the next visit. Not possible for the map currently'
        ' shown; unknown maps cause a warning and failure.')),
    ('CGiveInventoryItemActionBase', 'Who to give it to'): ('confirmed', '0x5b3b70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The object that receives the item; default "$Instigator". It must resolve to exactly one entity with hit'
        ' points, otherwise a warning is printed and nothing is given.')),
    ('CGiveCustomInventoryItemAction', 'Inventory Item'): ('confirmed', '0x5b3fd0, 0x5b4030', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The item, configured here in place, that is handed over. It must be of the same class as its '
        "definition's default item; otherwise a warning is printed and the action fails.")),
    ('CGiveDefaultInventoryItemAction', 'Inventory Item Definition'): ('confirmed', '0x5b4d90, 0x5b4ef0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Item type to give; the recipient gets the definition\'s default item (e.g. "Ore Deposits", "Key, Sun"). A'
        ' definition without a default item makes the action fail.')),
    ('CGiveMeSomePointsAction', 'Entity To Give Point To'): ('confirmed', '0x5a9fa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Object whose player gets the points (default "$Instigator"); it must resolve to exactly one object '
        'controlled by a player, otherwise nothing happens. The action always succeeds.')),
    ('CGiveMeSomePointsAction', 'Points To Give'): ('confirmed', '0x5a9fa0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Number of points added to that player's multiplayer score (default 1; negative values subtract).")),
    ('CGiveMyTeamAPointAction', 'Entity To Give Point To'): ('confirmed', '0x5a9c10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Object whose team gets one point in a team game (default "$Instigator"); it must resolve to exactly one '
        'object. In a game type without team scores nothing happens. The action always succeeds.')),
    ('CGiveTeamAPointAction', 'Team Number'): ('confirmed', '0x5a9950, 0x51bb90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The default (-1) addresses no team, so nothing happens until a team is chosen. Reaching the frag limit '
        'with the point ends the match.')),
    ('CHealthIsAtLeast', 'Name To Check For'): ('confirmed', '0x4c61c0, 0x4c6200', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects to check (names, comma lists, ranges, "$Trigger" etc.); only destructable entities count, others'
        ' cause a warning.')),
    ('CHealthIsAtLeast', 'Minimum Health'): ('confirmed', '0x4c6200', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hit points an object must have left to count (default 100). Despite the name the object needs strictly '
        'more than this value; inactive objects never count.')),
    ('CHealthIsAtLeast', 'Desired Minimum Count'): ('confirmed', '0x4c61c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action succeeds when at least this many of the objects have enough health (default 1).')),
    ('CHideAction', 'Target Name'): ('confirmed', '0x4c3020, 0x4c1920', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects to make invisible (names, comma lists, ranges, "$Trigger" etc.). They stay active and can still '
        'collide. Succeeds if at least one object was visible.')),
    ('CIfAction', 'If'): ('confirmed', '0x41bba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The condition: this action runs first; its result decides whether the second or the third action runs. '
        'Without it the whole action does nothing and fails.')),
    ('CIfAction', 'Then'): ('confirmed', '0x41bba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Runs when "If" succeeded; its result becomes the result of the whole action. Empty: the action simply '
        'succeeds.')),
    ('CIfAction', 'Else'): ('confirmed', '0x41bba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Runs when "If" failed. The whole action then always counts as failed, whatever this action returns.')),
    ('CImpersonateAction', 'Action'): ('confirmed', '0x4b7550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action that is run with a different trigger and instigator: "$Trigger" and "$Instigator" inside it then '
        'mean the objects named in "Trigger" and "Instigator". Its result is passed on; empty: succeeds.')),
    ('CImpersonateAction', 'Trigger'): ('confirmed', '0x4b7550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the object that acts as trigger for "Action" (default "$Trigger" = unchanged). It must resolve '
        'to exactly one object; otherwise a warning is printed and the action runs without a trigger.')),
    ('CImpersonateAction', 'Instigator'): ('confirmed', '0x4b7550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the object that acts as instigator for "Action" (default "$Instigator" = unchanged). It must '
        'resolve to exactly one object; otherwise a warning is printed and the action runs without an instigator.')),
    ('CIncrementCounterStatAction', 'Statistic To Increment'): ('confirmed', '0x555d90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only works in the single-player quest game; elsewhere the action fails.')),
    ('CIncrementMissionObjective', 'Objective Id Tag'): ('confirmed', '0x513f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'ID tag of the objective in the current mission that is counted up by one (for counting objectives such '
        'as "5 Korbo Slaves"). Afterwards the mission\'s completed action runs once all objectives are complete. '
        'Unknown tag or no mission: warning, failure.')),
    ('CIsAliveAction', 'Name To Check For'): ('confirmed', '0x4c5db0, 0x4c5df0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects to check (names, comma lists, ranges, "$Trigger" etc.). An object counts as alive when it is '
        'active and has hit points left (non-zero).')),
    ('CIsAliveAction', 'Desired Minimum Count'): ('confirmed', '0x4c5db0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action succeeds when at least this many of the objects are alive (default 1).')),
    ('CIsDoorClosedAction', 'Door Name'): ('confirmed', '0x4c42a0, 0x4bfb90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Doors to test (animated entities; names, comma lists etc.). Succeeds if at least one of them currently '
        'stands in the sequence "Closed".')),
    ('CIsDoorLockedAction', 'Door Name'): ('confirmed', '0x4c42a0, 0x4bfe50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Doors to test (animated entities). Succeeds if at least one of them has a door AI that is locked.')),
    ('CIsDoorOpenAction', 'Door Name'): ('confirmed', '0x4c42a0, 0x4bf8d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Doors to test (animated entities; names, comma lists etc.). Succeeds if at least one of them currently '
        'stands in the sequence "Open".')),
    ('CIsMissionObjectiveComplete', 'Objective Id Tag'): ('confirmed', '0x5146c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'ID tag of the objective in the current mission; the action succeeds when that objective is complete. '
        'Unknown tag or no mission: warning, failure.')),
    ('CIsMissionObjectiveDefined', 'Objective Id Tag'): ('confirmed', '0x514a40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'ID tag to look for; the action succeeds when the current mission has an objective with it (compared '
        'without regard to case). No warning when it is missing.')),
    ('CIsOnSameTeamAction', 'Entity To Check'): ('confirmed', '0x5a9100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'First object (default "$Instigator"); it must resolve to exactly one object. The action succeeds when '
        'both objects have the same team number (neutral objects count as one team).')),
    ('CIsOnSameTeamAction', 'Entity To Compare To'): ('confirmed', '0x5a9100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Second object (default "$Trigger"); it must resolve to exactly one object, otherwise the action fails.')),
    ('CIsOnTeamAction', 'Team Number'): ('confirmed', '0x5a8d70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action succeeds when the object\'s team number equals this value; the default "Nutral" (-1) tests for'
        ' neutral objects.')),
    ('CIsOnTeamAction', 'Entity To Check'): ('confirmed', '0x5a8d70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Object whose team is tested (default "$Instigator"); it must resolve to exactly one object, otherwise '
        'the action fails.')),
    ('CLockDoorAction', 'Door Name'): ('confirmed', '0x4bd600, 0x4bd340', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Doors to lock (names, comma lists etc.); each gets the lock message, which its door AI handles. Succeeds'
        ' if at least one door accepted it.')),
    ('CMultipleActionsAction', 'Action'): ('confirmed', '0x4b87a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'List of actions that all run one after the other in list order, with the same trigger and instigator. '
        'The whole action succeeds if at least one of them succeeded.')),
    ('CAndAction', 'Early Exit'): ('confirmed', '0x4ba290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked, the list stops at the first action that fails (the remaining ones do not run). The AND '
        'action succeeds only if every action succeeded.')),
    ('CMultipleDelayedActionsAction', 'Delay Between Actions'): ('confirmed', '0x4b8d00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Spacing in seconds: the first action runs at once, copies of the others are queued so that the n-th runs'
        ' n × this value later (default 1). The result is that of the first action.')),
    ('COrAction', 'Early Exit'): ('confirmed', '0x4bacf0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked, the list stops at the first action that succeeds (the remaining ones do not run). The OR '
        'action succeeds if any action succeeded.')),
    ('CSeriesAction', 'When Done'): ('confirmed', '0x4b9440', QT_TRANSLATE_NOOP(
        'fieldhelp', 'What happens when the series has run past its last action: "Repeat Series" starts again with the first, '
        '"Repeat Last Action" keeps running the last one, "Do Nothing" runs nothing more and fails.')),
    ('CSeriesAction', 'Require Success To Advance'): ('confirmed', '0x4b9440', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked (default), the series moves on to the next action only after the current one succeeded; a '
        'failed action is tried again next time. Unchecked: every run advances.')),
    ('CSeriesAction', 'Next Action Index'): ('confirmed', '0x4b9440', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the 0-based index of the action the series runs next. Leave it at 0 in a level; '
        'another value starts the series at that action.')),
    ('CXOrAction', 'Early Exit'): ('confirmed', '0x4ba7b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked, the list stops as soon as a second action succeeds (the XOR then fails at once). The XOR '
        'action succeeds only if exactly one action succeeded.')),
    ('CNotAction', 'Action'): ('confirmed', '0x4bb4f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action whose result is inverted: success becomes failure and vice versa. Empty: the NOT action succeeds.')),
    ('COffsetYSortAction', 'Target'): ('confirmed', '0x4c71d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Entities whose drawing order is shifted (names, comma lists, "$Trigger" etc.); objects that are not '
        'entities are skipped.')),
    ('COffsetYSortAction', 'Y Sort Offset'): ('confirmed', '0x4c71d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels added to the sorting line (Y sort) that decides which objects are drawn in front. Note: it '
        "changes the entity's model, so every entity using the same model is affected, and the offset adds up "
        'each time the action runs (use a negative value to undo).')),
    ('COnlyOnceAction', 'Action'): ('confirmed', '0x4b6cb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action that runs only the first time; it is then deleted from this object (and is missing in a save '
        'game). Later runs do nothing and fail.')),
    ('COnlyOnceEveryXSecondsAction', 'Action'): ('confirmed', '0x4b70f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action that runs at most once per "Min Time"; its result is passed on.')),
    ('COnlyOnceEveryXSecondsAction', 'Min Time'): ('confirmed', '0x4b70f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Minimum time in seconds of game time between two runs of "Action" (default 5).')),
    ('COnlyOnceEveryXSecondsAction', 'Next Alowable Time'): ('confirmed', '0x4b70f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the game time (seconds) from which "Action" may run again; leave it at 0 in a '
        'level (0 always allows).')),
    ('COnlyOnceEveryXSecondsAction', 'Fail Action'): ('confirmed', '0x4b70f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Optional action that runs instead when the action is triggered again too early; the whole action then '
        'fails.')),
    ('COtherMapAction', 'Action'): ('confirmed', '0x41f130, 0x41f6c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action that is stored and runs when the player next enters the map "Other Map Name" (without trigger or '
        'instigator). Several can be pending for one map.')),
    ('COtherMapAction', 'Other Map Name'): ('confirmed', '0x41f130', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Map for which "Action" is stored: path below "Levels/" without ".zax" (e.g. "Inside Ship", "ACT 2/M8/08 '
        'Pits Holding"; case does not matter, backslashes are corrected with a warning). An empty or unknown name'
        ' causes a warning and failure.')),
    ('CPainAction', 'Hit Points'): ('confirmed', '0x4c3ca0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage dealt to each target, in hit points (default 1).')),
    ('CPainAction', 'Damage Type'): ('confirmed', '0x4c3ca0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage type passed with the hit (e.g. "Normal", "Unavoidable"); how the target reacts (e.g. a matching '
        'shield) depends on it.')),
    ('CPainAction', 'Sound'): ('confirmed', '0x4c3ca0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played at each damaged target.')),
    ('CPainAction', 'Target'): ('confirmed', '0x4c3c70, 0x4c3ca0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Objects that take the damage (default "$Instigator"; names, comma lists, ranges, "$Touching" work). Only'
        ' destructable entities are hurt; the damage counts as coming from the instigator. Always succeeds.')),
    ('CPlayAnimationAction', 'Animation'): ('confirmed', '0x4bedc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the sequence to play once on each target (e.g. "Death", "switch"). Targets whose model lacks the'
        ' sequence do not play anything.')),
    ('CPlayAnimationAction', 'Target Name'): ('confirmed', '0x4bed90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animated entities that play the animation (names, comma lists, ranges, "$Trigger" etc.); other objects '
        'cause a warning.')),
    ('CPlayAnimationAction', 'When Done'): ('confirmed', '0x4bedc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'What the entity shows after the animation: "Stop on last frame" holds its last frame, "Return to First '
        'Frame" goes back to its first frame, "Previous Sequence" returns to the sequence it had before, "Set '
        'Sequence" switches to "End Sequence Name".')),
    ('CPlayAnimationAction', 'End Sequence Name'): ('confirmed', '0x4bedc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence the entity switches to after the animation; only used when "When Done" is "Set Sequence" '
        '(default "Idle").')),
    ('CPlayAnimationAction', 'Delay Between Targets'): ('confirmed', '0x4bed90, 0x41aed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'With several targets: seconds between the start on one target and the next (the first starts at once). 0'
        ' = all at the same time.')),
    ('CPlayAnimationAction', 'Play In Reverse'): ('confirmed', '0x4bedc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When checked, the animation plays backwards, from its last frame to its first.')),
    ('CPlaySoundAction', 'Sound'): ('confirmed', '0x4c01b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound to play.')),
    ('CPlaySoundAction', 'Position'): ('confirmed', '0x4c01b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Object at which the sound plays (default "$Trigger"), so its volume depends on the distance. If the name'
        ' resolves to no single object (a warning is printed), the sound plays for the whole level without '
        'position.')),
    ('CPlayVOAction', 'VO'): ('confirmed', '0x4c0ca0, 0x595be0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Voice-over recording to play on the voice-over channel; only when voice-overs are switched on in the '
        'options. Other sounds are lowered while it plays; it does not interrupt a voice-over of higher priority.'
        ' The action fails when nothing was played.')),
    ('CPositionedAction', 'Forward Position'): ('confirmed', '0x49c620, 0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Offset in pixels along the direction the object faces (aiming angle for animated entities), e.g. the '
        'muzzle distance in front of a character. Formerly "Arm Length".')),
    ('CPositionedAction', 'Lateral Position'): ('confirmed', '0x49c620, 0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Offset in pixels sideways to the facing direction (vertical parts squeezed by the isometric view ratio).'
        ' Formerly "Sholder Width".')),
    ('CPositionedAction', 'Height'): ('confirmed', '0x4c4ee0, 0x4c0950', QT_TRANSLATE_NOOP(
        'fieldhelp', "Height in pixels above the object's ground: added to the height of fired projectiles, and used to raise "
        'the test point when looking up the surface type. Formerly "Gun Height".')),
    ('CDischargeWeaponThisFrameBaseAction', 'Fire Up Angle'): ('confirmed', '0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Elevation of the shot in radians: the projectile's speed is split into a horizontal part (cosine) and an"
        ' upward part (sine). 0 = flat.')),
    ('CDischargeWeaponThisFrameBaseAction', 'Use This Pos To Aim'): ('confirmed', '0x4c4ee0, 0x49b1a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "When checked (default), the character remembers this muzzle position and the weapon's shoot sequence as "
        'its discharge point, which its aiming behaviours use to point the weapon at targets.')),
    ('CDischargeWeaponThisFrameAction', 'Use Primary'): ('confirmed', '0x5a7e20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Which weapon fires: checked (default) the current item of the "Primary" category, unchecked the current '
        '"Secondary" item of the character\'s inventory.')),
    ('CPlaySoundBySurfaceTypeAction', 'Default Sound'): ('confirmed', '0x4c0950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when the surface type at the test point has no entry in "Specializations".')),
    ('CPlaySoundBySurfaceTypeAction', 'Specializations'): ('confirmed', '0x4c0950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'List of surface type / sound pairs: the first entry whose surface type matches the ground at the test '
        'point (the position fields relative to the object) supplies the sound, e.g. different footstep sounds on'
        ' sand and metal.')),
    ('CPlaySoundBySurfaceTypeAction', 'Position Relative To'): ('confirmed', '0x4c0950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Object at which the test point is measured and the sound plays (default "$Trigger"). If it resolves to '
        'no single object, nothing plays.')),
    ('CPrintAction', 'Text'): ('confirmed', '0x5a6b30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Message shown on screen (translatable via Local.txt).')),
    ('CPrintAction', 'Display Method'): ('assumption', '0x5a6b30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Kind of HUD message: "Debug", "Ship" (default), "Zax", "OM" or "Other" (index 0-4 passed to the HUD\'s '
        "message display); assumed to select the message's look, e.g. by speaker.")),
    ('CRechargeShieldAction', 'Target'): ('confirmed', '0x56fd40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Characters whose shield is recharged (default "$Instigator"); other objects are skipped.')),
    ('CRechargeShieldAction', 'Damage Type'): ('confirmed', '0x56fd40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only the first shield item (in the "Shield" category) protecting against this damage type and not yet '
        'full is recharged.')),
    ('CRechargeShieldAction', 'Recharge Percent'): ('confirmed', '0x56fd40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Charge added as a percentage of the shield\'s maximum charge (default 1 %); only used when "Recharge '
        'Uints" is 0. For the player the amount is scaled by the world settings.')),
    ('CRechargeShieldAction', 'Recharge Uints'): ('confirmed', '0x56fd40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Fixed amount of charge (energy units, MJ) added to the shield; 0 (default) uses "Recharge Percent" '
        'instead. For the player the amount is scaled by the world settings.')),
    ('CRemoveAIAction', 'Target Name'): ('confirmed', '0x4c29c0, 0x41aed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts whose AI is removed. Accepts part names, comma lists, ranges like "Name#1-5#", "$Trigger", '
        '"$Instigator", "$Touching" and "$Target(...)".')),
    ('CRemoveAIAction', 'AI'): ('confirmed', '0x4c4a70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The AI class to remove: on each target the first AI of this class is marked done and goes away. Nothing '
        'happens on targets without such an AI.')),
    ('CRemoveAIAction', 'Delay Between Removes'): ('confirmed', '0x4c29c0, 0x41aed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds between the targets when the name matches several parts: the first is handled at once, the n-th '
        "n × delay later (copies of the action in the level's queue). 0 handles all at once.")),
    ('CRepeatAction', 'Number of Repetitions'): ('confirmed', '0x4b7fe0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How often "Action To Repeat" runs. 0 runs it not at all. The action succeeds when one of the runs done '
        'immediately succeeded.')),
    ('CRepeatAction', 'Action To Repeat'): ('confirmed', '0x4b7fe0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action that is repeated. Without one the repeat action does nothing and fails.')),
    ('CRepeatAction', 'Delay Between'): ('confirmed', '0x4b7fe0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds between the repetitions: the first runs at once, the i-th as a copy i × delay later from the '
        "level's queue. 0 runs all repetitions at once.")),
    ('CSayQuip', 'Quip Category'): ('confirmed', '0x55b050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The quip category (an entry of the "Quips" folder) whose voice lines may be said. The category\'s own '
        '"Condition" action must succeed first; then the probability decides, and the decision is sent to every '
        'machine.')),
    ('CSayQuip', 'Probablity Of Saying Quip'): ('confirmed', '0x55b050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only reached when the category\'s "Condition" succeeds.')),
    ('CSelectMission', 'Mission Id Tag'): ('confirmed', '0x513210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'ID tag of the mission (compared without case) that becomes the current mission; the time of the change '
        'is recorded. An unknown tag is reported and the action fails; an empty tag fails silently. Default '
        '"M00".')),
    ('CSendAIDoneMessage', 'Target'): ('confirmed', '0x56d420, 0x41aed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts that get the "AI done" message, which makes e.g. a series AI move on to its next AI. Accepts '
        'part names, comma lists, ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and '
        '"$Target(...)". Default "$Trigger".')),
    ('CSendMessageAction', 'Message'): ('confirmed', '0x4c6590', QT_TRANSLATE_NOOP(
        'fieldhelp', "Name of the message sent to each target (turned into a message id); the target's AIs react to it (e.g. a"
        ' door AI). An empty message sends nothing.')),
    ('CSendMessageAction', 'Target'): ('confirmed', '0x4c6560', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts that receive the message. Accepts part names, comma lists, ranges like "Name#1-5#", '
        '"$Trigger", "$Instigator", "$Touching" and "$Target(...)". Default "$Trigger". The action always counts '
        'as successful.')),
    ('CSetAttackAIAction', 'Attack AI'): ('confirmed', '0x574050, 0x577660', QT_TRANSLATE_NOOP(
        'fieldhelp', "Template of the attack AI: each target's skeleton AI (enemy state machine) gets a copy that replaces its"
        ' old attack AI; if it is attacking right now, it restarts in the new AI. Targets without a skeleton AI '
        'are skipped.')),
    ('CSetAttackAIAction', 'Target'): ('confirmed', '0x574050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The enemies whose attack AI is replaced. Accepts part names, comma lists, ranges like "Name#1-5#", '
        '"$Trigger", "$Instigator", "$Touching" and "$Target(...)". Default "$Trigger".')),
    ('CSetCategoryAction', 'Target Name'): ('confirmed', '0x4c3020, 0x4c2550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Accepts the usual name syntax (comma lists, ranges, "$Trigger", "$Instigator" …).')),
    ('CSetCategoryAction', 'New Category'): ('confirmed', '0x4c2550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The categories the targets get: all category bits (the lower 16 bits of the flags) are cleared first, '
        'then these are set. Categories decide e.g. who enemies target and what triggers react to.')),
    ('CSetCollidableAction', 'Target Name'): ('confirmed', '0x4c3020', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts whose collision is switched. Accepts part names, comma lists, ranges like "Name#1-5#", '
        '"$Trigger", "$Instigator", "$Touching" and "$Target(...)".')),
    ('CSetCollidableAction', 'Collidable'): ('confirmed', '0x4c1c60', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 makes the targets collideable (solid), 0 lets things pass through them (the part\'s "Collideable" '
        'flag). Default 1.')),
    ('CSetCompassTargetAction', 'New Compass Target'): ('confirmed', '0x5a44b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Name of the one part the compass points at from now on (stored in the level's save data). Empty clears "
        'the compass target.')),
    ('CSetCurSequenceAction', 'Sequence'): ('confirmed', '0x4bf230', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the model sequence (animation) the targets switch to. If a target has no such sequence, a '
        'warning is reported and the action fails; empty does nothing.')),
    ('CSetCurSequenceAction', 'Target Name'): ('confirmed', '0x4bf200', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The animated entities whose sequence is set; other parts are warned about and skipped. Accepts part '
        'names, comma lists, ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and "$Target(...)".')),
    ('CSetHomeAction', 'Actor'): ('confirmed', '0x4c7890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Must be characters: with a "New Home Position" the original does not check this and fails on other '
        'parts. Accepts the usual name syntax.')),
    ('CSetHomeAction', 'New Home Position'): ('confirmed', '0x4c7890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The marker must resolve to exactly one part (else a warning and no change). The home is where e.g. a '
        'guarding enemy returns to.')),
    ('CSetModelAction', 'Target Name'): ('confirmed', '0x4c2100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only entities are changed; other parts are warned about and skipped. Accepts the usual name syntax.')),
    ('CSetModelAction', 'New Model'): ('confirmed', '0x4c2130', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The model the targets get. A character that is firing or waiting for a shot stops doing so.')),
    ('CSetModelAction', 'New Child Model'): ('confirmed', '0x4c2130', QT_TRANSLATE_NOOP(
        'fieldhelp', "Applied to the target's first child only, and only when that child is an entity; empty leaves the child "
        'unchanged.')),
    ('CSetMusicAction', 'Mixer Data'): ('confirmed', '0x51dbd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The level music to switch to: the three songs (full mix, medium mix, ambient) and the cross-fade time in'
        " seconds (default 5) are copied into the game's music mixer; a changed song cross-fades.")),
    ('CSetPatrolAIAction', 'Patrol AI'): ('confirmed', '0x573950, 0x5775e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Template of the patrol AI: each target's skeleton AI gets a copy that replaces its old patrol AI; if it "
        'is patrolling right now, it restarts in the new AI. Targets without a skeleton AI are skipped.')),
    ('CSetPatrolAIAction', 'Target'): ('confirmed', '0x573950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The enemies whose patrol AI is replaced. Accepts part names, comma lists, ranges like "Name#1-5#", '
        '"$Trigger", "$Instigator", "$Touching" and "$Target(...)". Default "$Trigger".')),
    ('CSetPursueAIAction', 'Pursue AI'): ('confirmed', '0x573cd0, 0x577620', QT_TRANSLATE_NOOP(
        'fieldhelp', "Template of the pursue AI: each target's skeleton AI gets a copy that replaces its old pursue AI; if it "
        'is pursuing right now, it restarts in the new AI. Targets without a skeleton AI are skipped.')),
    ('CSetPursueAIAction', 'Target'): ('confirmed', '0x573cd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The enemies whose pursue AI is replaced. Accepts part names, comma lists, ranges like "Name#1-5#", '
        '"$Trigger", "$Instigator", "$Touching" and "$Target(...)". Default "$Trigger".')),
    ('CSetTargetAction', 'Target to attack'): ('confirmed', '0x574a80', QT_TRANSLATE_NOOP(
        'fieldhelp', "The one part the attackers go after, resolved in the attacker's level. It must currently be collideable;"
        ' otherwise nothing changes. Default "$Instigator".')),
    ('CSetTargetAction', 'Attacker'): ('confirmed', '0x574a80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The enemies whose skeleton AI gets the new target; parts without a skeleton AI are skipped. Accepts part'
        ' names, comma lists, ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and "$Target(...)".'
        ' Default "$Trigger".')),
    ('CSetTargetTypeAction', 'Entity Name'): ('confirmed', '0x574710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The enemies whose valid target categories are changed; parts without a skeleton AI are skipped. Accepts '
        'part names, comma lists, ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and '
        '"$Target(...)". Default "$Trigger".')),
    ('CSetTargetTypeAction', 'Valid Targets'): ('confirmed', '0x574710, 0x5776b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The categories the enemy may pick as targets from now on (replaces the skeleton AI\'s "Target Type" '
        "categories). The AI's state is reset so it re-evaluates its target.")),
    ('CShakeScreenAction', 'Time to Shake'): ('confirmed', '0x4c80d0, 0x4e9f00, 0x4e9f70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds the view of the level shakes. The shake has full strength for the first three quarters and fades'
        ' out linearly over the last quarter. Default 1.')),
    ('CShakeScreenAction', 'Pixels To Shake'): ('confirmed', '0x4e9f00, 0x4e9f70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Strength of the shake: an envelope whose value is the offset in pixels; every frame the view is moved by'
        ' that amount in a random direction.')),
    ('CShowAction', 'Target Name'): ('confirmed', '0x4c3020, 0x4c1660', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts that become visible (those already visible are left alone). Accepts part names, comma lists, '
        'ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and "$Target(...)".')),
    ('CSpawnEffectAction', 'Explosion Model'): ('confirmed', '0x4c36a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The model played as an effect (an explosion entity) at each target. Without a model the action does '
        'nothing.')),
    ('CSpawnEffectAction', 'Location Entity'): ('confirmed', '0x4c3020, 0x4c36a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts at whose position the effect appears (one effect per part). Accepts part names, comma lists, '
        'ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and "$Target(...)".')),
    ('CSpawnEffectAction', 'X Offset'): ('confirmed', '0x4c36a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Horizontal offset of the effect from the target's position, in pixels.")),
    ('CSpawnEffectAction', 'Y Offset'): ('confirmed', '0x4c36a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Vertical (map y) offset of the effect from the target's position, in pixels.")),
    ('CSpawnEffectAction', 'Height Offset'): ('confirmed', '0x4c36a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Height of the effect above the ground in pixels, added to the target's own height when the target is an "
        'entity.')),
    ('CSpawnEffectAction', 'Play Default Sound'): ('confirmed', '0x4c36a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 plays the effect model's own sound with the effect, 0 keeps it silent. Default 1.")),
    ('CSpawnEffectAction', 'Action to execute After Effect'): ('confirmed', '0x4c36a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Optional action run once the effect model's default sequence has played through once (its frame count "
        'divided by its frames per second); a copy is queued per target.')),
    ('CSucceedAction', 'Action'): ('confirmed', '0x4baff0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action that is run; whatever its result, this action always counts as successful (useful in '
        'conditions and series).')),
    ('CSwitchMapActionBase', 'New Map Name'): ('confirmed', '0x4c1060, 0x4c11a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Partial file name of the level to switch to (e.g. "ACT 1/M1m2/01 TargDens"). An unknown level is '
        'reported and nothing happens. Empty: the part is moved within the current level (animated entities '
        'only).')),
    ('CSwitchMapActionBase', 'New Location'): ('confirmed', '0x4c11a0, 0x5a5570', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the start point (usually a spawn point) in the target level where the part appears. "$return" '
        'goes back to the level and position the part came from last.')),
    ('CSwitchMapActionBase', 'Who To Switch'): ('confirmed', '0x4c1030', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts that are moved. Accepts part names, comma lists, ranges like "Name#1-5#", "$Trigger", '
        '"$Instigator", "$Touching" and "$Target(...)". Default "$Instigator".')),
    ('CSwitchMapAction', 'Return to map'): ('confirmed', '0x5a5570, 0x59b3a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'What happens to the level left behind in the level cache: "definitely soon" keeps it loaded, "probably '
        'soon" keeps it but lets it age out first, "unlikely soon" releases it, "never" expires it. "Invalid '
        'setting!" gives an error message, but the switch still happens. No switch takes place while a '
        'non-interactive sequence plays.')),
    ('CRelocateAction', 'Relative Position'): ('confirmed', '0x5a59f0, 0x5a5a50', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 keeps the part's offset from the trigger: it arrives at the same offset from the start point. 0 places"
        ' it exactly on the start point. Default 0.')),
    ('CTeleportAction', 'Warp Behavior'): ('confirmed', '0x5a5fa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Visual warp effect (a render effect behaviour) played on the instigator when it is an animated entity – '
        'the instigator, not "Who To Switch". "Teleporter.wav" plays in any case.')),
    ('CSwitchMusicTrackAction', 'Track'): ('confirmed', '0x51ded0, 0x51e520', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The music track to switch to: the full mix, medium mix or ambient song of the current level music '
        '(cross-faded). The game picks the track itself every frame by the action going on, so the switch may not'
        ' last.')),
    ('CTriggerRelayAction', 'Relay Name'): ('confirmed', '0x420290', QT_TRANSLATE_NOOP(
        'fieldhelp', "The relays to fire: each active target part with a relay AI runs that AI's action (with this action's "
        'trigger and instigator), unless the relay may fire only once and already did. Accepts part names, comma '
        'lists, ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and "$Target(...)".')),
    ('CUnlockDoorAction', 'Door Name'): ('confirmed', '0x4bd600, 0x4bd630', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The doors that get the unlock message; their door AI unlocks them. Accepts part names, comma lists, '
        'ranges like "Name#1-5#", "$Trigger", "$Instigator", "$Touching" and "$Target(...)".')),
    ('CUpdateMissionObjective', 'Objective Id Tag'): ('confirmed', '0x513b20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'ID tag of the objective in the current mission (compared without case). Without a current mission or '
        'with an unknown tag a warning is reported and the action fails.')),
    ('CUpdateMissionObjective', 'New Status'): ('confirmed', '0x513b20, 0x510e20, 0x510da0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The objective\'s new status text (a Local.txt key). A key containing "Complete" (but not "Incomplete") '
        'marks it complete, "Fail" failed; when all objectives are complete the mission\'s completed action runs. '
        'Default "Completed".')),
    ('CUseCannedAction', 'Canned Object'): ('verified', '0x468950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Entry of the canned objects (Resources/Canned Objects/*.can) whose action is run. With the canned '
        'object\'s "Use" set to "Shared Global Instance" the one shared action runs, with "Local Copy" a copy of '
        'it. Fails if the entry holds no action.')),
    ('CUseChargeFromInventoryItemAction', 'Inventory Item Definition'): ('confirmed', '0x5b56c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The energy item (by definition) in the player's inventory whose charge is used. If the player has no "
        'such energy item, the action fails.')),
    ('CUseChargeFromInventoryItemAction', 'Amount To Use'): ('confirmed', '0x5b56c0, 0x5afe60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Charge taken from the item. Only taken when the item holds at least that much; otherwise nothing is '
        'taken and the action fails (usable as a condition). Default 1.')),
    ('CWhileAction', 'Condition'): ('confirmed', '0x4b7bb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action tested before each round; "Action To Repeat" runs as long as it succeeds. After 100 successes the'
        ' loop stops with the warning "stuck in an infinite loop" and fails. Without a condition the action '
        'fails.')),
    ('CWhileAction', 'Action To Repeat'): ('confirmed', '0x4b7bb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action run each time the condition succeeds. The while action succeeds when it ran at least once.')),
    ('CXDoorAction', 'Door Name'): ('confirmed', '0x4bd830, 0x4bd870', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The doors to open, close or toggle (animated entities only; other parts are warned about). A door with a'
        ' door AI handles it itself; one without plays its "Opening"/"Closing" sequences directly, with a '
        'warning. Accepts part names, comma lists, ranges like "Name#1-5#", "$Trigger", "$Instigator", '
        '"$Touching" and "$Target(...)".')),
    ('CXDoorAction', 'Delay Between Doors'): ('confirmed', '0x4bd830, 0x41aed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds between the doors when the name matches several: the first now, the n-th n × delay later. 0 '
        'handles all at once.')),
    ('CActionQueue', 'Items'): ('confirmed', '0x41c700, 0x41c7a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the delayed actions of the level waiting to run (from delays between targets, '
        'repetitions, effects); each counts its time down and runs when due; leave unchanged in a level.')),
    ('CActionQueueItem', 'Time To Execute'): ('confirmed', '0x41c700', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left until the queued action runs; counted down every frame; leave '
        'unchanged in a level.')),
    ('CActionQueueItem', 'Action'): ('confirmed', '0x41c700', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the queued action (owned by the item); it runs once the time is up and the item is'
        ' removed; leave unchanged in a level.')),
    ('CActionQueueItem', 'Instigator'): ('confirmed', '0x41c120, 0x41c700, 0x41c230', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the instigator passed to the queued action; cleared when that part is deleted or '
        'leaves the level; leave unchanged in a level.')),
    ('CActionQueueItem', 'TriggerPart'): ('confirmed', '0x41c120, 0x41c700, 0x41c230', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the trigger part passed to the queued action; cleared when that part is deleted or'
        ' leaves the level; leave unchanged in a level.')),
    ('CActionQueueItem', 'TriggerAI'): ('confirmed', '0x41c120, 0x41c700, 0x41c230', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the trigger AI passed to the queued action; cleared when that part is deleted or '
        'leaves the level; leave unchanged in a level.')),
    ('CActionQueueItem', 'TargetPart'): ('confirmed', '0x41c120, 0x41c700, 0x41c230', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the one target the queued action works on (without one it runs normally on its '
        'names); cleared when that part is deleted or leaves the level; leave unchanged in a level.')),
    ('CAmbientSound', 'Ambient Sound Index'): ('confirmed', '0x4ee100, 0x4ee4e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: index of the looping sound in the sound list, set by the ambient sound AI that '
        'started it; -1 or an index beyond the list means none; leave unchanged in a level.')),
    ('CAmbientSound', 'Who Started'): ('confirmed', '0x4ee4a0, 0x4ee100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the part whose ambient sound AI started the sound; the sound follows its position '
        'and is muted while that part is in another level; leave unchanged in a level.')),
    ('CAmbientSound', 'Outer Ambient Radius'): ('confirmed', '0x4ee6e0, 0x4ee100', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: copy of the AI's outer radius in pixels, handed to the sound as its range together"
        ' with "Max Distance"; leave unchanged in a level.')),
    ('CAmbientSound', 'Max Distance'): ('confirmed', '0x4ee6e0, 0x4ee100', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: copy of the AI's maximum hearing distance in pixels; beyond the sound's range it "
        'is muted; leave unchanged in a level.')),
    ('CAmbientSound', 'Inner Ambient Radius'): ('confirmed', '0x4ee6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: copy of the AI\'s inner radius in pixels; only its square ("Inner Ambient Radius '
        'Sqrd") is used; leave unchanged in a level.')),
    ('CAmbientSound', 'Inner Ambient Radius Sqrd'): ('confirmed', '0x4ee100, 0x4ee6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: square of the inner radius; while the listener is within it the sound plays '
        "without direction (centred), outside it from the part's position; leave unchanged in a level.")),
    ('CAmbientSound', 'Muted'): ('confirmed', '0x4ee100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 while the sound is silenced because the listener is out of range or the part is '
        'in another level; leave unchanged in a level.')),
    ('CAmbientSound', 'ShouldBePlaying'): ('confirmed', '0x4ee100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 when the sound was started; a dropped sound is then started again when audible; '
        'leave unchanged in a level.')),
    ('CAnimationTrigger', 'Action'): ('confirmed', '0x560300, 0x560480', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the animation reaches this frame (the entity is trigger and instigator). Nothing fires '
        'while the game is not running.')),
    ('CAnimationTrigger', 'Trigger Forward'): ('confirmed', '0x560300, 0x560480', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 fires the action when the sequence plays forwards through this frame. Also used for the one frame '
        "fired when the entity's frame is locked, even when playing backwards (original quirk). Default 1.")),
    ('CAnimationTrigger', 'Trigger Reverse'): ('confirmed', '0x560480', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 fires the action when the sequence plays backwards through this frame. Default 1.')),
    ('CBroadcaster', 'Listener'): ('confirmed', '0x467d80', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved state in the older file format: objects listening to this part's messages; after loading they are "
        'turned into "Objects Listening" entries. Leave unchanged in a level.')),
    ('CBroadcaster', 'Objects Listening'): ('confirmed', '0x467d40, 0x467e60, 0x467ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: references to the objects (AIs, actions in the queue, sounds …) that get this '
        'part\'s messages such as "Delete" or "Died"; maintained by the game; leave unchanged in a level.')),
    ('CCannedObject', 'Object'): ('confirmed', '0x468950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The ready-made object (usually an action tree) this canned object holds; "CUseCannedAction" runs it when'
        ' it is an action.')),
    ('CCannedObject', 'Use'): ('verified', '0x468950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How "CUseCannedAction" uses the object: "Shared Global Instance" runs the one stored action every time, '
        '"Local Copy" runs a fresh copy per use action. All original files use "Shared Global Instance".')),
    ('CCategoryDefinition', 'MiniMap Color'): ('assumption', '0x46a3d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Colour of the category, presumably for the mini map. No game code reading it was found: the mini map '
        "draws its dots in the HUD options' colours. Default white; the original leaves one byte of the default "
        'uninitialised.')),
    ('CCharacterListHolder', 'Player'): ('confirmed', '0x59bd50, 0x4ef8f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the list of player characters held by the game (one per player); a character is '
        'removed from it when deleted; leave unchanged in a level.')),
    ('CChildList', 'Child List'): ('confirmed', '0x4fc7c0, 0x4fc7d0, 0x4c2130', QT_TRANSLATE_NOOP(
        'fieldhelp', "The part's child parts (owned), e.g. a torso model on a character or a muzzle flash; they belong to and "
        'are deleted with the parent. "CSetModelAction" changes the first child with "New Child Model".')),
    ('CContinuousFireWeaponData', 'Start Shooting Continuous Action'): ('confirmed', '0x472c90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run (for the shooting character) when a continuous fire weapon (e.g. a beam) starts firing.')),
    ('CContinuousFireWeaponData', 'Finish Shooting Continuous Action'): ('confirmed', '0x472dc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run (for the shooting character) when the continuous fire weapon stops firing.')),
    ('CContinuousFireWeaponData', 'Impact Exposion'): ('confirmed', '0x4735c0, 0x5b77a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model of the impact effect shown where the beam hits a target; hidden while nothing is hit.')),
    ('CContinuousFireWeaponData', 'Shoot Spread Angle'): ('confirmed', '0x474510, 0x5b78f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Full width of the beam's cone around the facing direction, in radians (shown in degrees; default 15°, up"
        ' to 180°). Targets inside the cone can be hit; a lightning beam also wanders within it.')),
    ('CContinuousFireWeaponData', 'Extra Close Range Strike Damage'): ('confirmed', '0x5b79f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Extra damage per second at point-blank range, falling linearly to 0 at the weapon's range; added to the "
        "weapon's strike damage. Default 15.")),
    ('CContinuousFireWeaponData', 'Looping Discharge Sound'): ('confirmed', '0x4735c0, 0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound looped at the shooter while the beam fires.')),
    ('CZaxCustomRules', 'Materials Generator Display'): ('confirmed', '0x5a1cd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Layout and colours of the materials generator window (also used by the voice log). These options are '
        "part of the game's custom rules (Rules.txt), not of a level.")),
    ('CZaxCustomRules', 'Inventory Display'): ('confirmed', '0x5a1d40, 0x429de0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Layout, colours and texts of the inventory screen and the HUD's item display. These options are part of "
        "the game's custom rules (Rules.txt), not of a level.")),
    ('CZaxCustomRules', 'Dialog Display'): ('confirmed', '0x5a1e80, 0x47bbd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Layout of the conversation window (portraits, text area, scroll speed, fonts) and the multiplayer chat '
        "fonts. These options are part of the game's custom rules (Rules.txt), not of a level.")),
    ('CZaxCustomRules', 'Main Menu Display'): ('confirmed', '0x5a1ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Layout of the main menu. These options are part of the game's custom rules (Rules.txt), not of a level.")),
    ('CZaxCustomRules', 'Player Walking Control Options'): ('confirmed', '0x5a1f40', QT_TRANSLATE_NOOP(
        'fieldhelp', "Settings of the player's walking control (movement by mouse and keys). These options are part of the "
        "game's custom rules (Rules.txt), not of a level.")),
    ('CZaxCustomRules', 'HUD Options'): ('confirmed', '0x5a1fa0, 0x508180', QT_TRANSLATE_NOOP(
        'fieldhelp', "Also holds the mini map's size, opacity and dot colours. These options are part of the game's custom "
        'rules (Rules.txt), not of a level.')),
    ('CZaxCustomRules', 'Mission Over Options'): ('confirmed', '0x5a2010', QT_TRANSLATE_NOOP(
        'fieldhelp', "These options are part of the game's custom rules (Rules.txt), not of a level.")),
    ('CZaxCustomRules', 'MultiPlayer Mission Over Options'): ('confirmed', '0x5a20d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Used instead of "Mission Over Options" when the window is opened in its multiplayer form. These options '
        "are part of the game's custom rules (Rules.txt), not of a level.")),
    ('CZaxCustomRules', 'Load Save Screen Options'): ('confirmed', '0x5a2190', QT_TRANSLATE_NOOP(
        'fieldhelp', "Holds only the colour of the screen's borders. These options are part of the game's custom rules "
        '(Rules.txt), not of a level.')),
    ('CZaxCustomRules', 'Sphere Of Zin Options'): ('confirmed', '0x5a21f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "These options are part of the game's custom rules (Rules.txt), not of a level.")),
    ('CCustomRulesList', 'Custom Rules List'): ('assumption', '0x5609f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A list of custom rules objects. The game\'s rules keep one without saving it and use their single "Custom'
        ' Rules" object instead; no use of the list beyond loading and freeing was found.')),
    ('CDamageTypeDefinition', 'Unavoidable damage'): ('confirmed', '0x56da70', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 means damage of this type cannot be absorbed by a shield; 0 lets a shield of this damage type absorb '
        'it. Default 0; none of the original damage types sets it.')),
    ('CDeathBehaviorListDefinition', 'Behaviors'): ('confirmed', '0x478260, 0x48cdf0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The entity behaviours (e.g. animations, effects) played in order when an entity with this death type '
        'dies; they run as a new AI on the dying entity.')),
    ('CDialogDisplayOptions', 'Default Chat Font'): ('confirmed', '0x59b260', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Default "Small Blue".')),
    ('CDialogDisplayOptions', 'Player Chat Font'): ('confirmed', '0x5ac390', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Default "Small Red".')),
    ('CDialogDisplayOptions', 'Background X'): ('confirmed', '0x47bbd0, 0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels of the window background image relative to the frame image; enlarges the window by '
        'the difference. Default 39.')),
    ('CDialogDisplayOptions', 'Background Y'): ('confirmed', '0x47bbd0, 0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position in pixels of the window background image relative to the frame image; enlarges the window by '
        'the difference. Default 53.')),
    ('CDialogDisplayOptions', 'Portrait X'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "X position in pixels of both speakers' portraits in the conversation window. Default 38.")),
    ('CDialogDisplayOptions', 'Portrait Y1'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position in pixels of the first speaker\'s portrait; the second is drawn "Portrait YDist" lower. '
        'Default 50.')),
    ('CDialogDisplayOptions', 'Portrait Y2'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Meant as the second portrait's y position in pixels. Not read by the conversation window (only saved and"
        ' loaded); the window uses "Portrait Y1" + "Portrait YDist" and the portrait image\'s own size. Default '
        '153.')),
    ('CDialogDisplayOptions', 'Portrait YDist'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Vertical distance in pixels between the first and the second speaker's portrait. Default 103.")),
    ('CDialogDisplayOptions', 'Portrait Width'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Meant as the portrait width in pixels. Not read by the conversation window (only saved and loaded); the '
        'window uses "Portrait Y1" + "Portrait YDist" and the portrait image\'s own size. Default 81.')),
    ('CDialogDisplayOptions', 'Portrait Height'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Meant as the portrait height in pixels. Not read by the conversation window (only saved and loaded); the'
        ' window uses "Portrait Y1" + "Portrait YDist" and the portrait image\'s own size. Default 77.')),
    ('CDialogDisplayOptions', 'Selection Light Upper X'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels of the selection light shown while the first (upper) speaker talks. Default 64.')),
    ('CDialogDisplayOptions', 'Selection Light Upper Y'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position in pixels of the selection light shown while the first (upper) speaker talks. Default 56.')),
    ('CDialogDisplayOptions', 'Selection Light Lower X'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels of the selection light shown while the second (lower) speaker talks. Default 64.')),
    ('CDialogDisplayOptions', 'Selection Light Lower Y'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position in pixels of the selection light shown while the second (lower) speaker talks. Default 142.')),
    ('CDialogDisplayOptions', 'Text X'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Left edge in pixels of the area in which the conversation lines scroll (lines are clipped to it). '
        'Default 144.')),
    ('CDialogDisplayOptions', 'Text Y'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Top edge in pixels of the area in which the conversation lines scroll. Default 43.')),
    ('CDialogDisplayOptions', 'Text Width'): ('confirmed', '0x47c2e0, 0x47cd20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the text area; lines are wrapped to it (less twice the window border). Default 382.')),
    ('CDialogDisplayOptions', 'Text Height'): ('confirmed', '0x47bbd0, 0x47c2e0, 0x47cfa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height in pixels of the text area; new text starts below it and scrolls up, and it enters the scroll '
        'speed computed for voiced lines. Default 216.')),
    ('CDialogDisplayOptions', 'Text Background X'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Left edge in pixels of the filled rectangle drawn behind the conversation text. Default 144.')),
    ('CDialogDisplayOptions', 'Text Background Y'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Top edge in pixels of the filled rectangle drawn behind the conversation text. Default 43.')),
    ('CDialogDisplayOptions', 'Text Background Width'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the filled rectangle drawn behind the conversation text. Default 382.')),
    ('CDialogDisplayOptions', 'Text Background Height'): ('confirmed', '0x47c2e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height in pixels of the filled rectangle drawn behind the conversation text. Default 216.')),
    ('CDialogDisplayOptions', 'Text Font'): ('confirmed', '0x47c2e0, 0x47cd20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the conversation lines (used for drawing, wrapping and line height).')),
    ('CDialogDisplayOptions', 'Max Scroll Rate'): ('confirmed', '0x47cfa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Fastest scroll speed in pixels per second for a voiced line; the speed is chosen so the line reaches the'
        ' top when the voice ends (at least 1). Default 35.')),
    ('CDialogDisplayOptions', 'Default Scroll Rate'): ('confirmed', '0x47cfa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Scroll speed in pixels per second for lines without a voice-over. Default 25.')),
    ('CDialogDisplayOptions', 'FileName Font'): ('assumption', '0x47d3b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A font setting that no code of the conversation window or the chat reads (only saved and loaded); its '
        'purpose is unknown.')),
    ('CDialogDisplayOptions', 'Close Button X Pos'): ('confirmed', '0x47bbd0', QT_TRANSLATE_NOOP(
        'fieldhelp', "X position in pixels of the window's close button. Default 488.")),
    ('CDialogDisplayOptions', 'Close Button Y Pos'): ('confirmed', '0x47bbd0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Y position in pixels of the window's close button. Default 4.")),
    ('CDialogLine', 'Name'): ('verified', '0x41e0f0, 0x54e490, 0x591bd0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Label of a line in a dialogue script (.RDS, the line ':Label'). „Line“ of a CZaxDialogAction names it; "
        'the lookup ignores case and takes the first label of that name. A name no action finds makes the game '
        'exit.')),
    ('CDialogLine', 'Text'): ('verified', '0x41e010, 0x5a4bd0, 0x41e0f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The text of the line. Text before the first ": " (if it starts within the first 20 characters) is the '
        'speaker, which also picks the portrait; the rest is the shown line. Trailing white space is removed.')),
    ('CEnergyMeter', 'Line Dim Color'): ('confirmed', '0x486d10, 0x4b3ab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Energy meter colour (HUD). Only used by a meter wider than tall: the top and bottom border lines, and '
        'the dark end of the gradient on the left and right end caps.')),
    ('CEnergyMeter', 'Line Bright Color'): ('confirmed', '0x486d10, 0x4b3ab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Energy meter colour (HUD). A meter taller than wide gets a 1-pixel frame in this colour; a wider one '
        "uses it as the bright middle of the end caps' gradient.")),
    ('CEnergyMeter', 'Charged Dim Color'): ('confirmed', '0x486d10, 0x4b3ab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Energy meter colour (HUD) of the filled part, dark end: only a meter wider than tall uses it, as a '
        'vertical gradient between this and „Charged Bright Color“ (bright at one third of the height).')),
    ('CEnergyMeter', 'Charged Bright Color'): ('confirmed', '0x486d10, 0x4b3ab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Energy meter colour (HUD) of the filled part: a meter taller than wide fills from the bottom in this '
        "colour on black; a wider one uses it as the bright line of the fill's gradient.")),
    ('CEnergyMeter', 'Under Charged Dim Color'): ('confirmed', '0x486d10, 0x4868a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "No effect in the game: the energy meter's drawing never reads this colour (only saved and loaded).")),
    ('CEnergyMeter', 'Under Charged Bright Color'): ('confirmed', '0x486d10, 0x4868a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "No effect in the game: the energy meter's drawing never reads this colour (only saved and loaded).")),
    ('CEntityBehaviorClearFlags', 'Visible'): ('confirmed', '0x497c10', QT_TRANSLATE_NOOP(
        'fieldhelp', "When set (1), the behaviour clears the object's flag „Visible“ as soon as it begins, then removes itself"
        ' from the behaviour stack. 0 leaves that flag alone.')),
    ('CEntityBehaviorClearFlags', 'Collideable'): ('confirmed', '0x497c10', QT_TRANSLATE_NOOP(
        'fieldhelp', "When set (1), the behaviour clears the object's flag „Collideable“ as soon as it begins, then removes "
        'itself from the behaviour stack. 0 leaves that flag alone.')),
    ('CEntityBehaviorClearFlags', 'Tries To Collide'): ('confirmed', '0x497c10', QT_TRANSLATE_NOOP(
        'fieldhelp', "When set (1), the behaviour clears the object's flag „Tries To Collide“ as soon as it begins, then "
        'removes itself from the behaviour stack. 0 leaves that flag alone.')),
    ('CEntityBehaviorClearFlags', 'Stationary'): ('confirmed', '0x497c10', QT_TRANSLATE_NOOP(
        'fieldhelp', "When set (1), the behaviour clears the object's flag „Stationary“ as soon as it begins, then removes "
        'itself from the behaviour stack. 0 leaves that flag alone.')),
    ('CEntityBehaviorClearFlags', 'Active'): ('confirmed', '0x497c10', QT_TRANSLATE_NOOP(
        'fieldhelp', "When set (1), the behaviour clears the object's flag „Active“ as soon as it begins, then removes itself "
        'from the behaviour stack. 0 leaves that flag alone.')),
    ('CEntityBehaviorExecuteAction', 'Action'): ('confirmed', '0x499790', QT_TRANSLATE_NOOP(
        'fieldhelp', "Action executed once when the behaviour begins, with the object as instigator in the object's layer. The"
        ' behaviour ends at its next update.')),
    ('CEntityBehaviorFireWeapon', 'Angle To Fire'): ('confirmed', '0x5ab360, 0x5ab390, 0x5ab300', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect in the game: the fire behaviours fire the current weapon in its own direction and never read '
        'this angle (only saved and loaded; the code creating them passes -1 or another value).')),
    ('CEntityBehaviorPlaySequenceLooped', 'Sequence'): ('confirmed', '0x499d10, 0x499d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence that is set (at frame 0) when the behaviour begins and then played in a loop at its own frames '
        "per second. Empty keeps the object's current sequence.")),
    ('CEntityBehaviorPlaySequenceLooped', 'Playing Backwards'): ('confirmed', '0x499d50', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 plays the loop backwards (from the end wrapping to the last frame). With „Ping Pong“ the game switches'
        ' this flag itself at each end. Ignored while „Synchronize“ is on.')),
    ('CEntityBehaviorPlaySequenceLooped', 'Ping Pong'): ('confirmed', '0x499d50', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 turns the playing direction at each end instead of jumping back to the start (forwards, then '
        'backwards, …). Ignored while „Synchronize“ is on.')),
    ('CEntityBehaviorPlaySequenceLooped', 'Synchronize'): ('confirmed', '0x499d50', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 takes the frame from the global game clock instead of advancing it per object, so all objects with '
        'this sequence show the same frame; backwards and ping pong are ignored then.')),
    ('CEntityBehaviorPlaySequenceLooped', 'Playing'): ('confirmed', '0x499d50, 0x499f30, 0x499d10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Whether the loop is running (1, default). Beginning the behaviour and the message „Start Animation“ set '
        'it; with 0 the frame stands still. Mostly saved run-time state.')),
    ('CEntityBehaviorPlaySequenceLooped', 'Stoping'): ('confirmed', '0x499f30, 0x499d50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set by the message „Stop Animation“; the loop then stops at its next end and the '
        'behaviour ends. Beginning or „Start Animation“ clears it.')),
    ('CEntityBehaviorQueue', 'Behavior'): ('confirmed', '0x586f10, 0x586ef0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The behaviours of the queue, run one after another: each begins when it becomes current and is updated '
        'until it reports done, then the next one follows. After the last one the queue is done; beginning it '
        'again restarts at the first.')),
    ('CEntityBehaviorQueue', 'Current Behavior'): ('confirmed', '0x586f10, 0x586ef0, 0x586fb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Index (from 0) of the behaviour currently running. A value at or past the end (default 2147483647) means'
        ' done: the next begin restarts at 0. Saved run-time state.')),
    ('CEntityBehaviorQueue', 'Changed Behavior'): ('confirmed', '0x586f10, 0x586f80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 means the current behaviour has not begun yet and gets its begin call before its'
        ' next update.')),
    ('CEntityBehaviorSetPlayRatio', 'New Play Ratio'): ('confirmed', '0x497530', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Play ratio given to the object when the behaviour begins (animation speed factor; walking characters '
        'also move faster or slower, negative plays backwards); the behaviour then removes itself. Values outside'
        ' -10..10 make the game report an error but are kept.')),
    ('CEntityBehaviorSetRotationSequence', 'Sequence'): ('confirmed', '0x4965b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence set on the object when the behaviour begins (it also clears „Stationary“); the behaviour then '
        'removes itself. If the model lacks the sequence, the behaviour fails and is dropped. Empty only clears '
        '„Stationary“.')),
    ('CEntityBehaviorPlaySequenceOnce', 'Speed To Play'): ('confirmed', '0x496ee0, 0x497010', QT_TRANSLATE_NOOP(
        'fieldhelp', "Factor on the sequence's frames per second (-100..100, default 1). Negative plays the sequence backwards"
        ' from its last frame; 0 ends the behaviour at once.')),
    ('CEntityBehaviorPlaySequenceOnce', 'Done Sequence'): ('confirmed', '0x497010', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence set when the played sequence has reached its end (default „Idle“). Empty leaves the object on '
        'the end frame of the played sequence.')),
    ('CEntityBehaviorPlaySequenceOnce', 'Done Frame'): ('confirmed', '0x497010', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Frame of „Done Sequence“ shown afterwards (from 0). -1 means its last frame; values past the end are '
        'clamped to the frame count.')),
    ('CEntityBehaviorPlaySequenceOnce', 'Was Stationary'): ('confirmed', '0x496ee0, 0x497010', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: whether the object had „Stationary“ when the behaviour began; it gets the flag '
        'back at the end.')),
    ('CEntityBehaviorPlaySequenceOnce', 'Old Play Ratio'): ('confirmed', '0x496ee0, 0x497270', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the object's play ratio before the behaviour (the behaviour sets it to 0 and moves"
        ' the frames itself); restored when the behaviour ends.')),
    ('CEntityBehaviorPlaySequenceOnce', 'Move With Sequence'): ('confirmed', '0x497010', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 moves a movable object by the motion stored in the sequence's frames while it plays (e.g. a jump or "
        'lunge); 0 plays it in place.')),
    ('CEntityBehaviorStateSetClosestTarget', 'Max Distance'): ('confirmed', '0x5867c0, 0x586820', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Search radius in pixels (default 300): on begin the nearest matching object within it (and within the '
        "vision cone) becomes the object's target.")),
    ('CEntityBehaviorStateSetClosestTarget', 'Vision Cone'): ('confirmed', '0x5867c0, 0x586760, 0x586820', QT_TRANSLATE_NOOP(
        'fieldhelp', "Full width of the search cone in degrees (1–360, default 90), centred on the object's facing; half of it"
        ' on each side.')),
    ('CEntityBehaviorStateSetClosestTarget', 'Must Be Collideable'): ('confirmed', '0x5867c0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default): only objects with „Collideable“ can become the target. Active objects are required in any '
        'case.')),
    ('CEntityBehaviorStateSetClosestTarget', 'Must Have HPs'): ('confirmed', '0x5867c0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default): only objects that have hit points can become the target.')),
    ('CEntityBehaviorStateSetClosestTarget', 'Valid Targets'): ('confirmed', '0x5867c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Object categories that may become the target (default „Player“).')),
    ('CEntityBehaviorTurnToAngleBase', 'Old Stationary Flag'): ('confirmed', '0x494680, 0x4946b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the object's „Stationary“ flag from before the turn (0 or 2097152); the turn "
        'clears the flag and restores it when done. Leave unchanged in a level.')),
    ('CEntityBehaviorTurnToTarget', 'Point Weapon At Target'): ('confirmed', '0x4960f0, 0x495ec0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 measures the angle from the weapon's position instead of the object's centre, so the weapon points at "
        'the target.')),
    ('CEntityBehaviorTurnToTarget', 'Turn to Target'): ('confirmed', '0x4960f0, 0x496040', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the object whose direction the aiming angle turns to. Forgotten when it is '
        'deleted, dies, leaves the scope, is out of reach or the turn is done.')),
    ('CEntityBehaviorTurnToTarget', 'Max Dist To Target'): ('confirmed', '0x4960f0, 0x495ec0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Distance in pixels (vertical distance scaled like the game's perspective): while the target is farther "
        'away the turn stops and the target is forgotten.')),
    ('CEntityBehaviorTurnToTarget', 'Target Must Be Visible'): ('confirmed', '0x495ec0, 0x4960f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect in the game: stored when the behaviour is made but never read (only saved and loaded).')),
    ('CEntityBehaviorTurnToAngle', 'Angle To Turn To'): ('confirmed', '0x495490, 0x4953a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Target movement angle (stored in radians, shown in degrees). The object turns towards it at its model's "
        'turn speed until it is within 0.1 radians; then the behaviour ends.')),
    ('CEntityBehaviorTurnToAngle', 'Facing Backwards'): ('confirmed', '0x495490, 0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect in the game: neither the turn nor the move behaviour reads this byte (only saved and loaded). '
        "The object's own „Facing Backwards“ is a different field.")),
    ('CEntityBehaviorMoveToPos', 'Idle Behavior'): ('confirmed', '0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the embedded idle behaviour the mover runs once it has arrived or found no way '
        '(plays the idle sequence and fidgets).')),
    ('CEntityBehaviorMoveToPos', 'Play Ratio'): ('confirmed', '0x430f20, 0x430390, 0x430a40', QT_TRANSLATE_NOOP(
        'fieldhelp', "Speed factor while moving (default 1): set as the object's play ratio every update, so a walker animates"
        " and moves faster or slower; a flier's speed is multiplied by it.")),
    ('CEntityBehaviorMoveToPos', 'Smooth Turning'): ('confirmed', '0x430f20, 0x430c70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect in the game: the update always behaves as if it were set (steering round obstacles and the '
        'small-angle filter are always on).')),
    ('CEntityBehaviorMoveToPos', 'Do Path Finding'): ('confirmed', '0x4303f0, 0x5386b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 (default): the way is searched over the level's way point network and a target spot blocked by an "
        'object fails the move. 0 heads straight for the target.')),
    ('CEntityBehaviorMoveToPos', 'Finished'): ('confirmed', '0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the move is over (arrived or no way); the behaviour then only runs its idle '
        'behaviour.')),
    ('CEntityBehaviorMoveToPos', 'Failed Last Path'): ('confirmed', '0x4303f0, 0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set when the last way search found no way to the target.')),
    ('CEntityBehaviorMoveToPos', 'Idle Begin Called'): ('confirmed', '0x430f20, 0x430390', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: whether the idle behaviour has begun already.')),
    ('CEntityBehaviorMoveToPos', 'Move To Rate'): ('confirmed', '0x4303f0, 0x430a40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the gait the move sequence was chosen for (0 walk, 1 run, 2 crouch); taken from '
        'the walking character each time the move is aimed.')),
    ('CEntityBehaviorMoveToPos', 'CurTargetNormalX'): ('confirmed', '0x430f20, 0x430c70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: X of the unit vector from the next way point back to where the leg started; used '
        'to detect passing the point and to steer.')),
    ('CEntityBehaviorMoveToPos', 'CurTargetNormalY'): ('confirmed', '0x430f20, 0x430c70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: Y of the unit vector from the next way point back to where the leg started; used '
        'to detect passing the point and to steer.')),
    ('CEntityBehaviorMoveToPos', 'Path Finding Params'): ('confirmed', '0x4303f0, 0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the current way found over the way point network (the points still ahead).')),
    ('CEntityBehaviorMoveToPos', 'Pos Moving From'): ('confirmed', '0x4303f0, 0x430c70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: start point of the current leg in pixels.')),
    ('CEntityBehaviorMoveToPos', 'Final Dest'): ('confirmed', '0x4303f0, 0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the final target point in pixels; set by whoever starts the move.')),
    ('CEntityBehaviorMoveToPos', 'Cur Dest Move To'): ('confirmed', '0x430f20, 0x430c70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the next way point the object heads for, in pixels.')),
    ('CEntityBehaviorMoveToPos', 'Last Neg Dist'): ('confirmed', '0x430c70, 0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the remaining distance along the leg at the last update; used to notice when the '
        'object stops getting nearer.')),
    ('CEntityBehaviorMoveToPos', 'NumTimesLostGound'): ('confirmed', '0x430c70, 0x4303f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: how often the object made no progress while facing the next point; after six times'
        ' the way is searched again.')),
    ('CEntityBehaviorMoveToPos', 'Path Collide Checker'): ('confirmed', '0x4303f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the helper that tests the target spot and the way for collisions during the way '
        'search.')),
    ('CEntityBehaviorMoveToPos', 'Sequence'): ('confirmed', '0x430940, 0x430a40', QT_TRANSLATE_NOOP(
        'fieldhelp', "Sequence played while moving instead of „Walk“/„Run“/„Crouch“ by gait. Empty (default) uses the gait's "
        'sequence; a name the model lacks is reported as an error.')),
    ('CEntityBehaviorWait', 'Num Seconds'): ('confirmed', '0x497f80, 0x4990e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Duration in seconds (default 1) before the behaviour ends. The idle behaviour, which builds on it, also '
        'ends after this time.')),
    ('CEntityBehaviorWait', 'Seconds Have Transitioned'): ('confirmed', '0x497f80, 0x498600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds elapsed so far; the behaviour ends once it reaches „Num Seconds“. Leave at'
        ' 0 in a level.')),
    ('CEntityBehaviorIdle', 'Override Fidget Options'): ('confirmed', '0x498fa0, 0x4990e0, 0x498e20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Fidget settings used instead of the model's own. Fidgets only happen at all when the model itself has "
        "fidget settings; empty uses the model's.")),
    ('CEntityBehaviorIdle', 'Current Fidget Data'): ('confirmed', '0x498e20, 0x4a0680', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the model's list of fidget sequences and which one was played last; made when "
        'needed.')),
    ('CEntityBehaviorIdle', 'Time Until Next Fidget'): ('confirmed', '0x498fa0, 0x4990e0, 0x4a02c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left until the next fidget; drawn at start (0.25 to 1.75 times the average'
        ' time) and after each fidget from the fidget settings.')),
    ('CEntityBehaviorIdle', 'FPS Play Ratio'): ('confirmed', '0x498fa0, 0x4990e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: random speed factor of the idle animation (0.9–1.1), drawn anew at each start so '
        'idling characters do not move in step.')),
    ('CEntityBehaviorIdle', 'Fidgeting'): ('confirmed', '0x4990e0, 0x498e20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 while a fidget sequence plays instead of the idle sequence.')),
    ('CEntityBehaviorTransition', 'Transition In Or Out'): ('confirmed', '0x498600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Direction of the fade: „Transition In“ fades the object in over „Num Seconds“, „Transition Out“ fades it'
        ' out.')),
    ('CEntityBehaviorWarpEffect', 'Warp In'): ('confirmed', '0x5aac90', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default) warps the object in: it fades in during the first third of „Warp Time“ while the effect dies'
        ' down afterwards. 0 warps it out: the effect builds up over two thirds, then the object fades out.')),
    ('CEntityBehaviorWarpEffect', 'Warp Time'): ('confirmed', '0x5aac90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Duration of the warp in seconds (default 1).')),
    ('CEntityBehaviorWarpEffect', 'Warp Effect'): ('confirmed', '0x5aac50, 0x5aac90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The render effect put on the object during the warp (default CSimpleWarpEffect); its strength is driven '
        "by the warp's progress and it is removed at the end.")),
    ('CEntityBehaviorWarpEffect', 'Cur Warp Time'): ('confirmed', '0x5aac90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds of the warp elapsed so far. Leave at 0 in a level.')),
    ('CEntityBehaviorWarpEffect', 'Was Stationary'): ('confirmed', '0x5aac50, 0x5aac90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: whether the object had „Stationary“ before the warp; the flag is set again at the '
        'end.')),
    ('CEntityBehaviorWarpEffect', 'WhoWereConnectedTo'): ('confirmed', '0x5aac50, 0x5aa760', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the object the effect was put on; the effect is taken off it when the behaviour is'
        ' deleted.')),
    ('CShootEntityBehavior', 'Play Sequence'): ('confirmed', '0x578240, 0x5780f0, 0x578120', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the shoot sequence currently playing (a play-once behaviour); deleted when the '
        'behaviour begins again.')),
    ('CEntityBehaviorStack', 'InProcess'): ('confirmed', '0x49a480, 0x49a760', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 when the top behaviour of the stack has begun.')),
    ('CEntityBehaviorStack', 'Blocking Priority'): ('confirmed', '0x49a560, 0x49a480', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Priority of what was pushed last (Idle, Interruptable, SouldComplete, MustComplete). A new behaviour '
        'with a lower priority is refused; at „MustComplete“ nothing new is accepted until the stack is empty. '
        'Falls back to „Idle“ when empty.')),
    ('CEntityBehaviorStack', 'BehaviorList'): ('confirmed', '0x49a480, 0x49a560', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the behaviours on the stack, the last one is on top and runs.')),
    ('CEnvelope', 'Start Value'): ('confirmed', '0x49d730, 0x49d660', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Value the envelope starts from (-10000..10000; units depend on the use, e.g. seconds, degrees, pixels). '
        'When the owner resets it, the value jumps here and runs towards „End Value“.')),
    ('CEnvelope', 'End Value'): ('confirmed', '0x49d660, 0x49d730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Value the envelope runs to; it stops exactly there, then „Ending Behavior“ decides what follows. Equal '
        'to „Start Value“ keeps a constant value.')),
    ('CEnvelope', 'Speed'): ('confirmed', '0x49d660', QT_TRANSLATE_NOOP(
        'fieldhelp', "Change of the value per second (in the value's units). Keep it positive: the direction towards the end "
        'value is chosen by the game; a negative speed runs away from the target and never arrives.')),
    ('CEnvelope', 'Ending Behavior'): ('confirmed', '0x49d660', QT_TRANSLATE_NOOP(
        'fieldhelp', 'What happens at the end: „Stop at end“ keeps the end value, „Restart from beginning“ jumps back to '
        '„Start Value“ and runs again, „Reverse Direction“ runs back and forth between both values.')),
    ('CEnvelope', 'Current Value'): ('confirmed', '0x49d660, 0x49d730, 0x52b5b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the envelope's present value; the owner's reset sets it to „Start Value“ (particle"
        ' emitters reset their envelopes when they start).')),
    ('CEnvelope', 'Using Start'): ('confirmed', '0x49d660, 0x49d730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 while the value runs towards „End Value“, 0 while it runs back to „Start Value“ '
        '(Reverse Direction). Set to 1 by a reset.')),
    ('CEnvelope', 'Direction'): ('confirmed', '0x49d660, 0x49d730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 or -1, the sign of the movement; a reset sets 1 when „End Value“ is above „Start'
        ' Value“, else -1.')),
    ('CFidgetSettings', 'Avg Time Between Fidgets'): ('confirmed', '0x4a02c0, 0x498fa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Average time in seconds (default 20) between two fidget animations of an idling character. The first '
        'wait after the idle starts is random between 0.25 and 1.75 times this value.')),
    ('CFidgetSettings', 'Fidget Variance'): ('confirmed', '0x4a02c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Spread of the waits after a fidget (default 4): 0 waits exactly the average time; larger values give a '
        'random wait from 0 upwards around the average, with occasional long waits.')),
    ('CFidgetSettings', 'Fidget Sequence Order'): ('confirmed', '0x4a0680', QT_TRANSLATE_NOOP(
        'fieldhelp', "Which of the model's „Fidget“ sequences plays (crouching: „FidgetCrouch“ ones): „First Sequence Only“, "
        '„Random Order“, „Never Same Twice Consecutively“ (reports an error with only one). Original bugs: '
        '„Shuffeled Order“ and „Special Shuffeled Order“ are not implemented (error, no fidget); „Sequential '
        'Order“ never advances and always plays the same one.')),
    ('CGroundTextureFrame', 'Damage'): ('confirmed', '0x48d7f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage in hit points per second (0–9999) to living objects whose centre stands on ground of this '
        "texture. Only with a „Damage Type“ other than none. Set in the texture's .txt file, not in levels.")),
    ('CGroundTextureFrame', 'Damage Type'): ('confirmed', '0x48d7f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage type of the ground damage; „!None“ (as in all shipped textures) switches the ground damage off.')),
    ('CGroundTextureFrame', 'Surface Type'): ('confirmed', '0x4e9e60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Surface of this ground texture (default „Generic“), e.g. for surface-dependent footstep sounds; it '
        'counts where no object at that point gives its own surface.')),
    ('CLayer', 'Save Data'): ('confirmed', '0x4ebe10, 0x4ec090', QT_TRANSLATE_NOOP(
        'fieldhelp', "The level's header (CLayerSaveData). A level file holds exactly this object's fields; it is not written "
        'as a separate field.')),
    ('CFrameOverlayOptions', 'Text Overlays'): ('confirmed', '0x4b52e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Texts drawn onto a full-screen image (a .foo file in „Resources/Frame Overlay Options“ named like the '
        "image, e.g. the demo's sell screens), each with font, position and wrapping.")),
    ('CFrameOverlayTextOverlay', 'Text Font'): ('confirmed', '0x4b52e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the text (default „Character Dialog“).')),
    ('CFrameOverlayTextOverlay', 'Text HotSpot Coordinates'): ('confirmed', '0x4b52e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the text on the image in pixels (x, y). Set it explicitly: the game gives it no default.')),
    ('CFrameOverlayTextOverlay', 'Text Wrapping Width'): ('confirmed', '0x4b52e0, 0x4a6790', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels at which the text wraps to the next line (default 128).')),
    ('CFrameOverlayTextOverlay', 'Text String'): ('confirmed', '0x4b52e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The text that is drawn.')),
    ('CFrameOverlayTextOverlay', 'Pixels Between Lines'): ('confirmed', '0x4b52e0, 0x4a6790', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Extra space between wrapped lines in pixels (default 2).')),
    ('CFrameOverlayTextOverlay', 'Justification'): ('confirmed', '0x4b52e0, 0x4a6790', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the text lines: left, centre or right (default left).')),
    ('CGameType', 'Game Name'): ('assumption', '0x4ce900', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the game mode (e.g. „Death Match“, „Quest“). No code reading it was found, so its use is assumed'
        ' (a display name).')),
    ('CGameType', 'Players Initial Inventory'): ('confirmed', '0x5433e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Inventory a player gets at every (re)spawn: the inventory is emptied and filled from this one. Empty (as'
        ' in quest mode) leaves the player without items after a respawn.')),
    ('CGameType', 'Default Player Model'): ('assumption', '0x4ce900', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model of the player character in this game mode (shipped: „Characters/Crater/Crater“ for quest, „Crater '
        'Multiplayer“ for the multiplayer modes). No code reading it was found, so its effect is assumed.')),
    ('CMultiPlayerGameType', 'Max Number of Teams'): ('confirmed', '0x51c010, 0x51bef0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only used when „Is Team Game“ is 1: the number of teams of the match, joining players go to the smallest'
        ' of them. „Unlimited“ (0) means up to 20 teams for the assignment.')),
    ('CMultiPlayerGameType', 'Is Team Game'): ('confirmed', '0x51bef0, 0x51c010, 0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In a team game a joining player goes to the smallest team (limited by „Max Number of Teams“), the score '
        'boards draw players in the blue/red team fonts and the team count is set for the match; otherwise every '
        'player gets a team of their own.')),
    ('CMultiPlayerGameType', 'All Teams Share Spawn Points'): ('confirmed', '0x468f20, 0x4f4950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A player spawning without a named start point then uses the Team Info (start points) of a randomly '
        "chosen team instead of their own team's.")),
    ('CMultiPlayerGameType', 'Have Taken the Lead'): ('confirmed', '0x51bda0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action executed when a player takes the lead (more points than every other player); it runs once per '
        'change, with that player as the current connection (e.g. for an announcement to them).')),
    ('CMultiPlayerGameType', 'Have Lost the Lead'): ('confirmed', '0x51bda0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action executed when a player falls behind (another player has more points); it runs once per change, '
        'with that player as the current connection (e.g. for an announcement to them).')),
    ('CMultiPlayerGameType', 'Have Tied For the Lead'): ('confirmed', '0x51bda0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action executed when a player ties with the best other player; it runs once per change, with that player'
        ' as the current connection (e.g. for an announcement to them).')),
    ('CMultiPlayerGameType', 'Default Mini-ScoreBoard Font'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the rule lines at the bottom of the mini score board (time limit, score limit). The player rows '
        'do not use it.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Headings Font'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Font of the mini score board's headings (Name, Ping, Score); in games without teams also the font of all"
        ' player rows.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Blue Team Font'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the rows of players of the first team (blue) on the mini score board; only in team games.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Red Team Font'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the rows of players of every other team (red) on the mini score board; only in team games.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Blue Flag Font'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the flag mark next to a player of the red team who carries a flag (i.e. the blue flag).')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Red Flag Font'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the flag mark next to a flag carrier who is not on the red team (i.e. the red flag).')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Blue Flag String'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the flag mark shown next to a red-team player carrying a flag (default „*“).')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Red Flag String'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the flag mark shown next to any other flag carrier (default „*“).')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Rank X'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels on the mini score board of the column with the rank number (no heading) (default '
        "10); the column's justification is relative to it.")),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Rank Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the mini score board column with the rank number (no heading) at its X position: left, '
        'centre or right.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Flag X'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels on the mini score board of the column with the flag mark (only for flag carriers) '
        "(default 12); the column's justification is relative to it.")),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Flag Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the mini score board column with the flag mark (only for flag carriers) at its X position: '
        'left, centre or right.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Name X'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels on the mini score board of the column with the player name and its heading (default'
        " 17); the column's justification is relative to it.")),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Name Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the mini score board column with the player name and its heading at its X position: left, '
        'centre or right.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Score X'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels on the mini score board of the column with the score and its heading (default 170);'
        " the column's justification is relative to it.")),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Score Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the mini score board column with the score and its heading at its X position: left, centre '
        'or right.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Ping X'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels on the mini score board of the column with the ping and its heading (default 100); '
        "the column's justification is relative to it.")),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Ping Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the mini score board column with the ping and its heading at its X position: left, centre '
        'or right.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard AltScore1 X'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels on the mini score board of the column with the first extra number of the game mode '
        "(only when not 0, no heading) (default 120); the column's justification is relative to it.")),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard AltScore1 Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the mini score board column with the first extra number of the game mode (only when not 0, '
        'no heading) at its X position: left, centre or right.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard AltScore2 X'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels on the mini score board of the column with the second extra number of the game mode'
        " (only when not 0, no heading) (default 140); the column's justification is relative to it.")),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard AltScore2 Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the mini score board column with the second extra number of the game mode (only when not 0,'
        ' no heading) at its X position: left, centre or right.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Rules Justification'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the rule lines (time and score limit) at the bottom of the mini score board: left (at „Line'
        ' Spacing“ pixels from the left edge), centre, or right (the same distance from the right edge).')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Line Spacing'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Extra pixels between the rows of the mini score board (default 2). Also used as the rule lines' distance"
        ' from the bottom and the side edge.')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Header Spacing'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Extra pixels between the heading row and the first player row of the mini score board (default 4).')),
    ('CMultiPlayerGameType', 'Mini-ScoreBoard Top'): ('confirmed', '0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Y position in pixels of the mini score board's heading row (default 2).")),
    ('CMultiPlayerGameType', 'Default End ScoreBoard Font'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No effect in the game: the end score board (shown when the match is over) never reads this font (only '
        'saved and loaded).')),
    ('CMultiPlayerGameType', 'End ScoreBoard Headings Font'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Font of the end score board's headings (Rank, Name, Score) shown when the match is over; in games "
        'without teams also the font of all player rows.')),
    ('CMultiPlayerGameType', 'End ScoreBoard Blue Team Font'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the end score board rows of players of the first team (blue); only in team games.')),
    ('CMultiPlayerGameType', 'End ScoreBoard Red Team Font'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the end score board rows of players of every other team (red); only in team games.')),
    ('CMultiPlayerGameType', 'End ScoreBoard Rank X'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "X position in pixels of the end score board's rank column and its heading, from the left edge of the "
        'table area in the match-over window (default 15).')),
    ('CMultiPlayerGameType', 'End ScoreBoard Rank Justification'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Alignment of the end score board's rank column at its X position: left, centre or right.")),
    ('CMultiPlayerGameType', 'End ScoreBoard Name X'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "X position in pixels of the end score board's name column and its heading, from the left edge of the "
        'table area in the match-over window (default 70).')),
    ('CMultiPlayerGameType', 'End ScoreBoard Name Justification'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Alignment of the end score board's name column at its X position: left, centre or right.")),
    ('CMultiPlayerGameType', 'End ScoreBoard Score X'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "X position in pixels of the end score board's score column and its heading, from the left edge of the "
        'table area in the match-over window (default 140).')),
    ('CMultiPlayerGameType', 'End ScoreBoard Score Justification'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Alignment of the end score board's score column at its X position: left, centre or right.")),
    ('CMultiPlayerGameType', 'End ScoreBoard Line Spacing'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Extra pixels between the player rows of the end score board (default 2).')),
    ('CMultiPlayerGameType', 'End ScoreBoard Header Spacing'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Extra pixels between the heading row and the first player row of the end score board (default 4).')),
    ('CMultiPlayerGameType', 'End ScoreBoard Top'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Y offset in pixels of the end score board's heading row below the top of the table area (default 2).")),
    ('CCaptureTheFlagGameType', 'Capture Count Font'): ('confirmed', '0x4698f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the team score lines on the Capture the Flag HUD: one line per team (team name right-aligned, '
        "then its capture count) and a last line with the local player's own score.")),
    ('CCaptureTheFlagGameType', 'Capture Count Location'): ('confirmed', '0x4698f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Position in pixels of the team score lines, relative to the game type's area of the HUD bar; the team "
        'names end at this x and the numbers start there, each further line one font height lower. Default 270, '
        '14.')),
    ('CCaptureTheFlagGameType', 'Team Color Overlay Location'): ('confirmed', '0x4698f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position in pixels where the team overlay image ("Blue Team Overlay" or "Red Team Overlay", by the local'
        " player's team) is drawn, relative to the game type's area of the HUD bar. Default 185, 10.")),
    ('CCaptureTheFlagGameType', 'Blue Team Overlay'): ('confirmed', '0x4698f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Image shown on the HUD at "Team Color Overlay Location" while the local player is in team 0 (blue).')),
    ('CCaptureTheFlagGameType', 'Red Team Overlay'): ('confirmed', '0x4698f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Image shown on the HUD at "Team Color Overlay Location" while the local player is in any team other than'
        ' 0 (normally team 1, red).')),
    ('CCaptureTheFlagGameType', 'Force Team Colors On Players'): ('confirmed', '0x4698b0, 0x5abe70', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 (default): when a client sends its player colours, the first colour (the "New Hue 1" of the '
        'character\'s hue remap) is replaced by "Blue Team Hue" for team 0 or "Red Team Hue" for team 1; the '
        "second colour stays the player's choice. 0: players keep their own colours.")),
    ('CCaptureTheFlagGameType', 'Blue Team Hue'): ('confirmed', '0x4698b0, 0x5abe70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hue in degrees (0–360) forced on team 0 players\' first colour while "Force Team Colors On Players" is '
        'set. Default 215.')),
    ('CCaptureTheFlagGameType', 'Red Team Hue'): ('confirmed', '0x4698b0, 0x5abe70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hue in degrees (0–360) forced on team 1 players\' first colour while "Force Team Colors On Players" is '
        'set. Default 0.')),
    ('CDeathMatchGameType', 'Frags Font'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the local player\'s own frag count on the Death Match HUD (centred on "Frags Location"). Default '
        '"Number Grn".')),
    ('CDeathMatchGameType', 'Frags Location'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Centre point in pixels of the player's frag count, relative to the game type's area of the HUD bar. "
        'Default 348, 31.')),
    ('CDeathMatchGameType', 'Rankings Font'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the ranking table on the Death Match HUD (rank, name and frags of the leading players). Default '
        '"Small Green".')),
    ('CDeathMatchGameType', 'Rankings Location'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Top-left point in pixels of the HUD ranking table, relative to the game type's area of the HUD bar; the "
        '"Hud RankBoard … X" columns are offsets from its x. Default 190, 12.')),
    ('CDeathMatchGameType', 'Rankings Max Players'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of rows the HUD ranking table shows at most (fewer when fewer players are ranked). Default 4.')),
    ('CDeathMatchGameType', 'Rankings Space Between Lines'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Extra pixels between two rows of the HUD ranking table, added to the font's line height. Default 2.")),
    ('CDeathMatchGameType', 'Hud RankBoard Rank X'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal offset in pixels of the rank number column from "Rankings Location". Default 0.')),
    ('CDeathMatchGameType', 'Hud RankBoard Rank Justification'): ('confirmed', '0x4796a0, 0x4a6470', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the rank numbers are aligned at their column x: left (text starts there), centre or right (text ends'
        ' there). Default left.')),
    ('CDeathMatchGameType', 'Hud RankBoard Name X'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal offset in pixels of the player name column from "Rankings Location". Default 76.')),
    ('CDeathMatchGameType', 'Hud RankBoard Name Justification'): ('confirmed', '0x4796a0, 0x4a6470', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the player names are aligned at their column x: left, centre or right. Default right (names end at '
        'the column x).')),
    ('CDeathMatchGameType', 'Hud RankBoard Score X'): ('confirmed', '0x4796a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal offset in pixels of the frag count column from "Rankings Location". Default 80.')),
    ('CDeathMatchGameType', 'Hud RankBoard Score Justification'): ('confirmed', '0x4796a0, 0x4a6470', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the frag counts are aligned at their column x: left, centre or right. Default left.')),
    ('CSalvageKingGameType', 'Ore Points Value'): ('confirmed', '0x561ab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Points per unit of "Ore Deposits" when a Salvage King score-minerals action runs for a player: the '
        "player's ore is converted into score (count × value) and removed from the inventory. Default 1. Reaching"
        " the net game's frag limit ends the match.")),
    ('CSalvageKingGameType', 'Crystal Points Value'): ('confirmed', '0x561ab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Points per unit of "Crystals" when a Salvage King score-minerals action runs for a player: the crystals '
        'are converted into score (count × value) and removed from the inventory. Default 3.')),
    ('CSalvageKingGameType', 'Frags Font'): ('confirmed', '0x561760', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the local player\'s score on the Salvage King HUD (centred on "Frags Location"); despite the name'
        ' it shows the mineral score. Default "Number Grn".')),
    ('CSalvageKingGameType', 'Frags Location'): ('confirmed', '0x561760', QT_TRANSLATE_NOOP(
        'fieldhelp', "Centre point in pixels of the player's score on the Salvage King HUD, relative to the game type's area "
        'of the HUD bar. Default 348, 31.')),
    ('CQuestGameType', 'Column Options List'): ('confirmed', '0x5533e0, 0x50dc10, 0x5525e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The columns of the statistics table in the single-player mission-over window: column 0 the statistic's "
        'name, 1 and 2 its two values (this mission and the total), 3 the points (only shown when the statistics '
        'are scored). Each column has heading, value format, heading font, x offset, width and justification.')),
    ('CQuestGameType', 'Row Options List'): ('confirmed', '0x552730, 0x5533e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "One entry per statistic (in the order of the game's statistic names: ore collected, crystals collected, "
        'enemies killed, elapsed time, …): whether and how it is shown in the mission-over table, its label and '
        'fonts and its point weighting.')),
    ('CQuestGameType', 'Par Score Label Format'): ('confirmed', '0x5533e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Built-in default is " (typical)"; QuestMode.ZGT sets "(par %s)". The par row is drawn under a '
        "statistic's row in column 0 unless the statistic hides it.")),
    ('CQuestGameType', 'Scroll Rate'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Speed at which the statistics table scrolls upward in the mission-over window when it does not fit; the '
        'table repeats seamlessly. The value is in pixels per millisecond (the code multiplies it with the '
        'millisecond tick count), although the editor labels it pixels per second. Default 0.01 (= 10 pixels per '
        'second).')),
    ('CHudBarOptions', 'MiniMap Origin'): ('confirmed', '0x59e730, 0x508180', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The map is drawn at this offset from the top-left of the "NEWMINIMAP" frame image while that frame '
        'slides in with the HUD. Default 13, 17.')),
    ('CHudBarOptions', 'MiniMap Size'): ('confirmed', '0x508180, 0x4ec280, 0x4ed150', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width and height in pixels of the mini-map frame; also the size of every layer's mini-map image and "
        'fog-of-war image, into which the level is scaled. Default 155 × 95.')),
    ('CHudBarOptions', 'MiniMap Deploy Time'): ('confirmed', '0x5084a0, 0x507f40, 0x508000', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds; the same timer is used when the inventory panel hides and restores the map. Default 0.33.')),
    ('CHudBarOptions', 'MiniMap Open Sound'): ('confirmed', '0x5084a0, 0x5085f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when the mini-map window starts to slide open (toggle, or coming back after the inventory '
        'panel). Default "Inventory Up.wav".')),
    ('CHudBarOptions', 'MiniMap Close Sound'): ('confirmed', '0x5084a0, 0x508570', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when the mini-map window starts to slide closed (toggle, or when the inventory panel '
        'opens). Default "Sounds/Inventory Down.wav".')),
    ('CHudBarOptions', 'Max Zoom Factor'): ('confirmed', '0x59fd80, 0x4ec280', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The level (without its mini-map clipping) is divided by this value, then shrunk further if it still does'
        ' not fit "MiniMap Size"; so one map pixel covers at least this many level pixels. Default 48.')),
    ('CHudBarOptions', 'MiniMap Background Color'): ('confirmed', '0x59fe70, 0x4ed150, 0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Each layer's fog-of-war image and mini-map image start filled with this colour; explored parts of the "
        'fog are cleared. In multiplayer games the mini-map window shows the mini score board on this colour '
        'instead of the map.')),
    ('CHudBarOptions', 'MiniMap Player Color'): ('confirmed', '0x508180', QT_TRANSLATE_NOOP(
        'fieldhelp', "A 3 × 3 pixel dot at the first character's position.")),
    ('CHudBarOptions', 'MiniMap Intrest Color'): ('confirmed', '0x508180', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A 3 × 3 pixel dot for every object the layer monitors as a point of interest.')),
    ('CHudBarOptions', 'Fog Of War Update Distance'): ('confirmed', '0x508000', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The fog of war around the view is uncovered again when the view has moved more than this from where it '
        'was last uncovered, or the layer changed. The value is compared with the squared distance (pixels²): the'
        ' default 4096 means 64 pixels. -1 ("Always Update") uncovers every frame.')),
    ('CHudBarOptions', 'Mini-Map Opacity'): ('confirmed', '0x508180', QT_TRANSLATE_NOOP(
        'fieldhelp', '0–1; multiplied with the current opacity when the finished map is drawn onto the HUD. Default 0.8.')),
    ('CHueRemapHolder', 'Source Hue 1'): ('confirmed', '0x4d4ce0, 0x43c0e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hue in degrees (0–360) of the colours that the first remap replaces: every pixel of the figure whose hue'
        ' lies within "Error 1" of it gets "New Hue 1", keeping its lightness and saturation. Default 268 '
        '(purple).')),
    ('CHueRemapHolder', 'New Hue 1'): ('confirmed', '0x43c0e0, 0x5abe70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hue in degrees (0–360) given to the colours matched by "Source Hue 1"/"Error 1". In multiplayer it is '
        "set from the player's first chosen colour (or the team hue in Capture the Flag). Default 0 (red).")),
    ('CHueRemapHolder', 'Error 1'): ('confirmed', '0x43c0e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Tolerance in degrees (0–100) around "Source Hue 1": hues up to this far away on either side are '
        'remapped. Default 8.')),
    ('CHueRemapHolder', 'Source Hue 2'): ('confirmed', '0x4d4ce0, 0x43c410', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hue in degrees (0–360) of the colours that the second remap replaces (applied after the first, '
        'independently): pixels within "Error 2" of it get "New Hue 2". Default 160 (green).')),
    ('CHueRemapHolder', 'New Hue 2'): ('confirmed', '0x43c410, 0x5abe70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hue in degrees (0–360) given to the colours matched by "Source Hue 2"/"Error 2". In multiplayer it is '
        "set from the player's second chosen colour. Default 180.")),
    ('CHueRemapHolder', 'Error 2'): ('confirmed', '0x43c410', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Tolerance in degrees (0–100) around "Source Hue 2": hues up to this far away on either side are '
        'remapped. Default 4.')),
    ('CInventory', 'Inventory List'): ('confirmed', '0x4259b0, 0x424fd0, 0x426090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The items the figure carries (its starting inventory in a level). Each category (Primary, Secondary, '
        'Health, …) selects its first item automatically when none is selected; picking up items adds to this '
        'list.')),
    ('CInventory', 'Discovered Items'): ('confirmed', '0x426690, 0x426650', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Item types (catalogue entries) the figure has discovered. Items that require discovery can only be built'
        ' in the materials generator once listed here; each new discovery counts in the quest statistic of '
        'discovered items.')),
    ('CInventory', 'Disposed Items'): ('confirmed', '0x426090, 0x424fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: items just removed from the inventory, kept until the next update deletes them; '
        'leave empty in a level.')),
    ('CInventory', 'Item In Focus'): ('confirmed', '0x426070, 0x4259b0, 0x4da290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: index in "Inventory List" of the item highlighted in the inventory screen (-1 '
        'none); set to each newly added item and corrected when it is out of range. Leave unchanged in a level.')),
    ('CInventory', 'Item Type Info'): ('confirmed', '0x425290, 0x4262e0, 0x424fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state, one entry per item category: the selected item, the item being changed to and the '
        'change timers. Leave unchanged in a level; inconsistent entries are repaired.')),
    ('CInventory', 'Properly Inited'): ('confirmed', '0x424fd0, 0x4262e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time flag: 1 once the inventory has selected each category's first item and checked its lists."
        ' With 0 that happens on the first update. Leave unchanged in a level.')),
    ('CAnimationOverlayInventoryDetailRenderer', 'Detail Image'): ('confirmed', '0x5adea0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animated sequence (from the detail image list) drawn in the inventory screen over the item picture at '
        'the inventory page\'s "Detail Image X/Y", playing in time with the game clock.')),
    ('CAnimationOverlayInventoryDetailRenderer', 'Next Renderer'): ('confirmed', '0x5adea0, 0x5ae060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Another detail renderer drawn after this overlay; its text line is also what the item list shows for the'
        ' item (none: no text).')),
    ('CCountInventoryDetailRenderer', 'Format'): ('confirmed', '0x5b12d0, 0x5b1440', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The text is drawn centred 45 pixels right of and 20 pixels below the detail position, and is also the '
        "item's text line.")),
    ('CCountInventoryDetailRenderer', 'Font'): ('confirmed', '0x5b12d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the count text in the inventory detail view.')),
    ('CDeployableInventoryDetailRenderer', 'Format'): ('confirmed', '0x47af90, 0x47b150', QT_TRANSLATE_NOOP(
        'fieldhelp', "Text shown in the inventory detail view for a deployable item; its %d is replaced by the item's value "
        '(its damage fraction, judging by the default text) times 100, %% gives a percent sign. Drawn centred at '
        '45, 20 pixels from the detail position and used as the item\'s text line. Default "Damage: %d%%".')),
    ('CDeployableInventoryDetailRenderer', 'Font'): ('confirmed', '0x47af90', QT_TRANSLATE_NOOP(
        'fieldhelp', "Font of the deployable's damage text in the inventory detail view.")),
    ('CEnergyTextInventoryDetailRenderer', 'Singular Format'): ('confirmed', '0x4843e0, 0x4845d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text used for an energy item whose charge is at most 1; %s is replaced by the charge printed with '
        '"Digits Of Precision" decimals. Drawn centred at 45, 20 pixels from the detail position and used as the '
        'item\'s text line. Default "%s Mj".')),
    ('CEnergyTextInventoryDetailRenderer', 'Plural Format'): ('confirmed', '0x4843e0, 0x4845d0, 0x484740', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text used for an energy item whose charge is above 1; %s is replaced by the charge printed with "Digits '
        'Of Precision" decimals. Default "%s Mj". Older files with a single "Format" are converted into both '
        'formats on loading.')),
    ('CEnergyTextInventoryDetailRenderer', 'Digits Of Precision'): ('confirmed', '0x4843e0, 0x4845d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of decimal places (0–9) of the charge in the energy text. Default 1.')),
    ('CEnergyTextInventoryDetailRenderer', 'Font'): ('confirmed', '0x4843e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the energy text in the inventory detail view.')),
    ('CRandomOverlayInventoryDetailRenderer', 'Detail Image'): ('confirmed', '0x5ae480', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence (from the detail image list) of which a random frame is drawn over the item picture at the '
        'inventory page\'s "Detail Image X/Y"; a new random frame is picked once per frame time of the sequence (1'
        ' / its frame rate).')),
    ('CRandomOverlayInventoryDetailRenderer', 'Next Renderer'): ('confirmed', '0x5ae480, 0x5ae060', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Another detail renderer drawn after this overlay; its text line is also what the item list shows for the'
        ' item (none: no text).')),
    ('CSegmentedInventoryDetailRenderer', 'Completed Item'): ('confirmed', '0x56a6b0, 0x5698a0, 0x569b70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Item (catalogue entry) the player receives once all "Segments" are collected; the segmented item is then'
        ' removed. The segmented item can only be picked up while the completed item could be.')),
    ('CSegmentedInventoryDetailRenderer', 'Segments'): ('confirmed', '0x5698a0, 0x569b70, 0x56a3a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The parts needed for completion, as images of the detail image list; they identify the parts and every '
        "collected part's image is drawn (animated) at the detail position. The item is complete when it holds as"
        ' many parts as listed here.')),
    ('CSegmentedInventoryDetailRenderer', 'Compleated Action'): ('confirmed', '0x5698a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Runs right after the completed item is given, with the picking-up figure as instigator; nothing happens '
        'when the completed item cannot be taken.')),
    ('CSphereOfZinEnergyInventoryDetailRenderer', 'Detail Image'): ('confirmed', '0x582ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Sequence drawn at the detail position whose frame shows the Sphere of Zin's charge: the frame index "
        'follows the charge ratio plus a sine pulse; for anything but an energy item frame 0 is shown.')),
    ('CSphereOfZinEnergyInventoryDetailRenderer', 'Next Renderer'): ('confirmed', '0x582ee0, 0x583140', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Another detail renderer drawn after the sphere image; its text line is used for the item list, otherwise'
        ' "charge/capacity" is shown.')),
    ('CSphereOfZinEnergyInventoryDetailRenderer', 'Max Energy-Pulse Percentage'): ('confirmed', '0x582ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Pulse amplitude, as a fraction (0–1) of the sequence's frames, when the sphere is fully charged; between"
        ' empty and full it is interpolated towards "Min Energy-Pulse Percentage". Default 0.1.')),
    ('CSphereOfZinEnergyInventoryDetailRenderer', 'Min Energy-Pulse Percentage'): ('confirmed', '0x582ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Pulse amplitude, as a fraction (0–1) of the sequence's frames, when the sphere is empty. Default 0.015.")),
    ('CSphereOfZinEnergyInventoryDetailRenderer', 'Max Energy-Pulse Rate'): ('confirmed', '0x582ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pulse speed in cycles per second when the sphere is fully charged; interpolated towards "Min '
        'Energy-Pulse Rate" for lower charge. Default 2.')),
    ('CSphereOfZinEnergyInventoryDetailRenderer', 'Min Energy-Pulse Rate'): ('confirmed', '0x582ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pulse speed in cycles per second when the sphere is empty. Default 0.25.')),
    ('CSphereOfZinEnergyInventoryDetailRenderer', 'Flip HUD Sequence Order'): ('confirmed', '0x582ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the frame order of "Detail Image" is reversed (last frame for empty instead of the first). Default 0.')),
    ('CWeaponInventoryDetailRenderer', 'Warn Getting Low Threshold'): ('confirmed', '0x5ad650', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shot count at or below which the weapon\'s line in the inventory item list uses the "getting low" colour '
        '(0 shots: the "empty" colour); above it the normal colour. Counts the ammunition in the inventory, or '
        'the shots the battery allows for energy weapons. Default 5.')),
    ('CInventoryDisplayOptions', 'Page Area Left'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The inventory panel is 640 × 200 pixels; the three tab pages (inventory, mission, voice log) share this '
        'area.')),
    ('CInventoryDisplayOptions', 'Close Button X'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', "X position in pixels of the inventory panel's close button, relative to the panel. Default 609.")),
    ('CInventoryDisplayOptions', 'Close Button Y'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', "Y position in pixels of the inventory panel's close button, relative to the panel. Default 8.")),
    ('CInventoryDisplayOptions', 'Primary Font'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the inventory panel window (used for its own texts such as the tab buttons). Default "Character '
        'Dialog".')),
    ('CInventoryDisplayOptions', 'Inventory Button X'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels of the "Inventory" tab button, relative to the inventory panel. Default 529.')),
    ('CInventoryDisplayOptions', 'Inventory Button Y'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position in pixels of the "Inventory" tab button, relative to the inventory panel. Default 45.')),
    ('CInventoryDisplayOptions', 'Mission Button X'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels of the "Mission" tab button, relative to the inventory panel. Default 529.')),
    ('CInventoryDisplayOptions', 'Mission Button Y'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position in pixels of the "Mission" tab button, relative to the inventory panel. Default 82.')),
    ('CInventoryDisplayOptions', 'Voice Log Button X'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position in pixels of the "Voice Log" tab button, relative to the inventory panel. Default 529.')),
    ('CInventoryDisplayOptions', 'Voice Log Button Y'): ('confirmed', '0x428c00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position in pixels of the "Voice Log" tab button, relative to the inventory panel. Default 119.')),
    ('CInventoryDisplayOptions', 'Inventory Page'): ('confirmed', '0x4dabd0, 0x4dbd50, 0x4da290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Layout options of the inventory tab page: detail image, item statistics, buttons, item grid and scroll '
        'bar.')),
    ('CInventoryDisplayOptions', 'Mission Page'): ('confirmed', '0x5101d0, 0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Layout options of the mission tab page of the inventory panel (title, objectives list).')),
    ('CInventoryDisplayOptions', 'Voice Log Page'): ('confirmed', '0x5950c0, 0x595210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Layout options of the voice log tab page of the inventory panel (title, message list).')),
    ('CInventoryDisplayOptions', 'Primary Weapon Text Offset'): ('confirmed', '0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the ammunition count of a "Primary" weapon on the HUD, relative to the weapon\'s HUD position'
        ' (text centred there). For continuous-fire weapons the "+N" spare count is drawn left-aligned at this '
        'offset plus the meter width.')),
    ('CInventoryDisplayOptions', 'Secondary Weapon Text Offset'): ('confirmed', '0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the ammunition count of a non-primary (secondary) weapon on the HUD, relative to the '
        "weapon's HUD position (text centred there).")),
    ('CInventoryDisplayOptions', 'Amo Font'): ('confirmed', '0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the weapons\' ammunition counts on the HUD. Default "Small Green".')),
    ('CInventoryDisplayOptions', 'Time Position'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', "Position of the game type's match time (h:m:s) on the HUD, shown while no log or item message is "
        'displayed. HUD positions: x from the left edge of the HUD (on 800-pixel-wide screens shifted right by '
        'the spacer image), y counted upward from the bottom edge of the HUD.')),
    ('CInventoryDisplayOptions', 'Time Font'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the match time on the HUD. Default "Small Green".')),
    ('CInventoryDisplayOptions', 'Health Icon Position'): ('confirmed', '0x59e730, 0x4293c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the "Health Indicator Icon" image on the HUD (x not shifted on wide screens; y counted '
        'upward from the bottom edge of the HUD).')),
    ('CInventoryDisplayOptions', 'Health Text Position'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', "Position of the player's health number on the HUD (x not shifted on wide screens; y counted upward from "
        'the bottom edge of the HUD).')),
    ('CInventoryDisplayOptions', 'Health Font'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the health number on the HUD. Default "Small Red".')),
    ('CInventoryDisplayOptions', 'Ore Icon Position'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the "Ore Icon Small" image on the HUD; ore and crystal counts are only shown in the quest '
        '(single-player) and Salvage King game types. HUD positions: x from the left edge of the HUD (on '
        '800-pixel-wide screens shifted right by the spacer image), y counted upward from the bottom edge of the '
        'HUD.')),
    ('CInventoryDisplayOptions', 'Ore Text Position'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the ore text ("<name> = <count>", with "/<max>" when a maximum is set) on the HUD. HUD '
        'positions: x from the left edge of the HUD (on 800-pixel-wide screens shifted right by the spacer '
        'image), y counted upward from the bottom edge of the HUD.')),
    ('CInventoryDisplayOptions', 'Crystals Icon Position'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the "Crystal Icon Small" image on the HUD (quest and Salvage King only). HUD positions: x '
        'from the left edge of the HUD (on 800-pixel-wide screens shifted right by the spacer image), y counted '
        'upward from the bottom edge of the HUD.')),
    ('CInventoryDisplayOptions', 'Crystals Text Position'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the crystal text ("<name> = <count>", with "/<max>" when a maximum is set) on the HUD. HUD '
        'positions: x from the left edge of the HUD (on 800-pixel-wide screens shifted right by the spacer '
        'image), y counted upward from the bottom edge of the HUD.')),
    ('CInventoryDisplayOptions', 'Mineral Count Font'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the ore and crystal counts on the HUD. Default "Small Green".')),
    ('CInventoryDisplayOptions', 'Weapon Power Offset'): ('confirmed', '0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Top-left corner of a weapon's energy/charge meter on the HUD, relative to the weapon's HUD position. No "
        'default value is set.')),
    ('CInventoryDisplayOptions', 'Weapon Power Size'): ('confirmed', '0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width and height in pixels of a weapon's energy/charge meter on the HUD. Default 12 × 40.")),
    ('CInventoryDisplayOptions', 'Checked Item Icon Position'): ('confirmed', '0x59e730, 0x5a34b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the item icon of the item message (an item that is needed, used or named) on the HUD. HUD '
        'positions: x from the left edge of the HUD (on 800-pixel-wide screens shifted right by the spacer '
        'image), y counted upward from the bottom edge of the HUD.')),
    ('CInventoryDisplayOptions', 'Checked Item Text Offset'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Offset of the item message text from the item icon (x to the right, y downward); the text is centred '
        'there.')),
    ('CInventoryDisplayOptions', 'Checked Item Needed Text'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the item message when an item is needed. Default "Needed".')),
    ('CInventoryDisplayOptions', 'Checked Item Used Text'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the item message when an item was used. Default "Used".')),
    ('CInventoryDisplayOptions', 'Checked Item Needed Font'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the "needed" item message. Default "Small Red".')),
    ('CInventoryDisplayOptions', 'Checked Item Used Font'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the "used" item message and of the message that shows the item\'s name. Default "Small Green".')),
    ('CInventoryDisplayOptions', 'Checked Item Display Duration'): ('confirmed', '0x5a34b0, 0x5a3600, 0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds an item message stays on the HUD; the log-updated messages use the same duration. Default 2.')),
    ('CInventoryDisplayOptions', 'Log Updated Position'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the log message lines (centred) on the HUD; they take precedence over the item message and '
        'the time. HUD positions: x from the left edge of the HUD (on 800-pixel-wide screens shifted right by the'
        ' spacer image), y counted upward from the bottom edge of the HUD. Default 425, 30.')),
    ('CInventoryDisplayOptions', 'Log Updated Font'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the log messages on the HUD. Default "Small Green".')),
    ('CInventoryDisplayOptions', 'Log Updated Text'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'First line of every log message on the HUD. Default "Log Updated:".')),
    ('CInventoryDisplayOptions', 'Log Mission Objective Added Text'): ('confirmed', '0x59e730, 0x5a3600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Second line of the log message when a mission objective was added. Default "Added".')),
    ('CInventoryDisplayOptions', 'Log Mission Objective Completed Text'): ('confirmed', '0x59e730, 0x5a3600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Second line of the log message when a mission objective was completed. Default "Completed".')),
    ('CInventoryDisplayOptions', 'Press Key Prompt Text'): ('confirmed', '0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Last line of the log messages; %s is replaced by the name of the key bound to the logs control. Default '
        '"Press \'%s\' for Logs".')),
    ('CInventoryDisplayPageOptions', 'Detail Image X'): ('confirmed', '0x4dbd50, 0x5adea0, 0x5ae480', QT_TRANSLATE_NOOP(
        'fieldhelp', "The item's picture is drawn with its top-left corner here (relative to the inventory page); the overlay "
        'detail renderers draw at the same point.')),
    ('CInventoryDisplayPageOptions', 'Detail Image Width'): ('confirmed', '0x4d85d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No reader was found in the reimplemented code besides loading and saving; the picture is drawn at its '
        'own size.')),
    ('CInventoryDisplayPageOptions', 'Detail Image Height'): ('confirmed', '0x4d85d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No reader was found in the reimplemented code besides loading and saving; the picture is drawn at its '
        'own size.')),
    ('CInventoryDisplayPageOptions', 'Detail Stats X'): ('confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', "The item's name is drawn left-aligned at this point; the detail renderer's statistics start 1.5 "
        'name-font lines below it, and the description (Info button) is wrapped from here, inset by "Detail Stats'
        ' Margin".')),
    ('CInventoryDisplayPageOptions', 'Detail Stats Y'): ('confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'See "Detail Stats X": the name line\'s y; statistics and description start 1.5 name-font lines lower.')),
    ('CInventoryDisplayPageOptions', 'Detail Stats Width'): ('confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only used as the wrapping width of the item description: this width minus twice "Detail Stats Margin".')),
    ('CInventoryDisplayPageOptions', 'Detail Stats Height'): ('confirmed', '0x4d85d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No reader was found in the reimplemented code besides loading and saving.')),
    ('CInventoryDisplayPageOptions', 'Detail Stats Margin'): ('confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Inset of the item description from "Detail Stats X/Y" on the left and top, and on both sides of "Detail '
        'Stats Width".')),
    ('CInventoryDisplayPageOptions', 'Ammo Font'): ('confirmed', '0x5ad0e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Used for a weapon's ammunition line (ammunition name and count, or the energy source's charge).")),
    ('CInventoryDisplayPageOptions', 'Energy Font'): ('confirmed', '0x5ad0e0, 0x5b2160', QT_TRANSLATE_NOOP(
        'fieldhelp', "Used for the energy per shot of a weapon without ammunition and for a charger's charge text.")),
    ('CInventoryDisplayPageOptions', 'Damage Font'): ('confirmed', '0x5ad0e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Used for a weapon's projectile damage line.")),
    ('CInventoryDisplayPageOptions', 'Quantity Font'): ('confirmed', '0x5b1c60, 0x5b2580', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Used for the mineral count text and the health item text.')),
    ('CInventoryDisplayPageOptions', 'Detail Item Name Font'): ('confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Its line height also sets where the statistics and the description start (1.5 lines below the name).')),
    ('CInventoryDisplayPageOptions', 'Detail Info Font'): ('confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The description is shown while the Info button is pressed, in place of the picture and statistics.')),
    ('CInventoryDisplayPageOptions', 'Button Spacing'): ('confirmed', '0x4db170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The buttons are stacked vertically: each further button is placed this many pixels below the previous '
        'one.')),
    ('CInventoryDisplayPageOptions', 'Inner Select Color'): ('confirmed', '0x4da290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Drawn as a rectangle 1 pixel inside the outer one around the item in focus in the item grid.')),
    ('CInventoryDisplayPageOptions', 'Outer Select Color'): ('confirmed', '0x4da290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Drawn as a rectangle of "Icon Size" around the item in focus in the item grid.')),
    ('CInventoryDisplayPageOptions', 'List Width'): ('confirmed', '0x4dabd0, 0x4da290, 0x4da910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Also the number of cells per row used for keyboard and mouse navigation; the grid scrolls when the '
        'inventory has more rows than "List Height".')),
    ('CInventoryDisplayPageOptions', 'List Height'): ('confirmed', '0x4dabd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of visible rows; more rows are reached with the scroll bar.')),
    ('CInventoryDisplayPageOptions', 'Icon Size'): ('confirmed', '0x4da290, 0x4dabd0, 0x4da840', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Each grid cell is this size plus a 1-pixel grid line.')),
    ('CInventoryDisplayPageOptions', 'Icon Count Font'): ('confirmed', '0x4da290', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The count is only drawn when the inventory holds more than one of the item.')),
    ('CInventoryDisplayPageOptions', 'Icon Count X Position'): ('confirmed', '0x4da290', QT_TRANSLATE_NOOP(
        'fieldhelp', "Offset from the cell's top-left corner; the number is left-aligned there.")),
    ('CInventoryHUDRenderData', 'Opacity'): ('confirmed', '0x5aca10, 0x5acab0, 0x429980', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time HUD state: how opaque the item's icon is drawn (0..1); the renderer sets it every frame, and "
        'while the player switches items of a category the old and new item fade between 1 and 0. Not stored in '
        'levels.')),
    ('CInventoryHUDRenderData', 'Definition Index'): ('confirmed', '0x5aca30, 0x423c50, 0x581d20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: the item catalogue entry this HUD element shows; the renderer copies it from the '
        "player's item every frame and uses it to find the item's definition and screen position. Not stored in "
        'levels.')),
    ('CInventoryHUDRenderData', 'Changed Status'): ('confirmed', '0x5ac8a0, 0x5ac950, 0x5aca00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time network state: bit flags of what changed since the last network update (1 opacity, 2 catalogue '
        'entry); only changed values are sent, then the bits are cleared. Default 3 (everything). Leave '
        'unchanged.')),
    ('CCompassRenderData', 'Display Frame'): ('confirmed', '0x423990, 0x423c50, 0x423520', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: 1 while the compass needle is shown, i.e. a compass target is known and the overlay '
        'sequence has at least two frames; 0 hides it. Recomputed every frame.')),
    ('CCompassRenderData', 'Frame Changed'): ('confirmed', '0x423990, 0x423520, 0x4235d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time network state: set when the shown compass frame changed, so the next network update sends the '
        'new frame number; cleared after sending. Leave unchanged.')),
    ('CCompassRenderData', 'Any Change'): ('confirmed', '0x423990, 0x423650, 0x423520', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time network state: set when visibility or frame of the compass changed since the last network '
        'update; cleared after sending. Leave unchanged.')),
    ('CCompassRenderData', 'Frame Number'): ('confirmed', '0x423990, 0x423c50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: the frame of the compass\'s "HUD Overlay" sequence that points to the target (1 to '
        'frames - 1, from the angle between player and target). Recomputed every frame.')),
    ('CEnergyHUDRenderData', 'Capacity'): ('confirmed', '0x581a90, 0x581d20, 0x56ef20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: the most charge of the shown energy item (its definition\'s "Energy"), used as the '
        'full value of the energy meter. Recomputed every frame.')),
    ('CEnergyHUDRenderData', 'Charge'): ('confirmed', '0x581a90, 0x581d20, 0x56f280', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: the current charge of the shown energy item, drawn as the filled part of the energy '
        'meter. Recomputed every frame.')),
    ('CEnergyHUDRenderData', 'EnergyChanged Status'): ('confirmed', '0x581710, 0x5817a0, 0x581840', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time network state: bit flags of what changed since the last network update (1 capacity, 2 charge); '
        'cleared after sending. Default 3. Leave unchanged.')),
    ('CShieldHUDRenderData', 'Sheild List'): ('confirmed', '0x56ef20, 0x56ec50, 0x56f280', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: one energy entry (charge, capacity, catalogue entry) per shield item the player '
        'carries, rebuilt every frame; each is drawn as its own meter with a "charge/capacity" text.')),
    ('CShieldHUDRenderData', 'Old ListSize'): ('confirmed', '0x56ea30, 0x56eb00, 0x56ec00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time network state: the shield count at the last network update, used to tell which list entries are'
        ' new; set after each send. Leave unchanged.')),
    ('CWeaponHUDRenderData', 'Rounds'): ('confirmed', '0x4859b0, 0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: the rounds of ammunition the player has for the shown weapon, drawn as a number next'
        ' to the weapon icon. Recomputed every frame.')),
    ('CWeaponHUDRenderData', 'Continuous Fire Rounds'): ('confirmed', '0x4859b0, 0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time HUD state: for a continuous fire weapon the charge of its energy source; whole units are shown '
        'as "+N", the fraction in the item\'s energy meter. Recomputed every frame.')),
    ('CWeaponHUDRenderData', 'Batt Capacity'): ('confirmed', '0x4859b0, 0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time HUD state: for a weapon without ammunition the most charge of the player's battery (0 without "
        "one), the full value of the weapon's meter. Recomputed every frame.")),
    ('CWeaponHUDRenderData', 'Batt Charge'): ('confirmed', '0x4859b0, 0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time HUD state: for a weapon without ammunition the current charge of the player's battery, drawn in"
        " the weapon's meter. Recomputed every frame.")),
    ('CWeaponHUDRenderData', 'WeaponChanged Status'): ('confirmed', '0x4851e0, 0x485550, 0x485700', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time network state: bit flags of what changed since the last network update (1 rounds, 2 battery '
        'capacity, 4 battery charge); cleared after sending. Default 7. Leave unchanged.')),
    ('CCompassRenderer', 'HUD Overlay'): ('confirmed', '0x423990, 0x423c50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'HUD sequence of the compass needle: frame 0 is skipped, frames 1 to the last cover the full circle and '
        'the one pointing to the compass target is drawn with a pulsing opacity under the item icon. Needs at '
        'least two frames; the needle is hidden while no target is set.')),
    ('CCharacterInventoryHUDRenderer', 'Font'): ('confirmed', '0x582270', QT_TRANSLATE_NOOP(
        'fieldhelp', "Font for the name of the character's special ability, drawn centred on the item's HUD position over its "
        'energy meter.')),
    ('CSphereOfZinEnergyInventoryHUDRenderer', 'HUD Sequence'): ('confirmed', '0x583860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'HUD sequence of the Sphere of Zin display: the shown frame follows the charge ratio (empty = first '
        'frames, full = last frames) and swings around it like a sine pulse.')),
    ('CSphereOfZinEnergyInventoryHUDRenderer', 'Max Energy-Pulse Percentage'): ('confirmed', '0x583860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Strength of the pulse at full charge, as a fraction of the sequence (0..1; half of it is the swing to '
        'each side); between empty and full the strength is interpolated towards "Min Energy-Pulse Percentage". '
        'Default 0.1.')),
    ('CSphereOfZinEnergyInventoryHUDRenderer', 'Min Energy-Pulse Percentage'): ('confirmed', '0x583860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Strength of the pulse when empty, as a fraction of the sequence (0..1). Default 0.015.')),
    ('CSphereOfZinEnergyInventoryHUDRenderer', 'Max Energy-Pulse Rate'): ('confirmed', '0x583860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pulses per second at full charge; between empty and full the rate is interpolated towards "Min '
        'Energy-Pulse Rate". Default 2.')),
    ('CSphereOfZinEnergyInventoryHUDRenderer', 'Min Energy-Pulse Rate'): ('confirmed', '0x583860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pulses per second when empty. Default 0.25.')),
    ('CSphereOfZinEnergyInventoryHUDRenderer', 'Flip HUD Sequence Order'): ('confirmed', '0x583860', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 counts the frames of "HUD Sequence" backwards, so a full charge shows the first frames. Default 0.')),
    ('CSphereOfZinEnergyInventoryHUDRenderer', 'Overlay HUD Sequence'): ('confirmed', '0x583860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Optional second HUD sequence drawn over the pulsing one at the same position, played in a loop at its '
        'own frame rate. Empty: none.')),
    ('CFlagInventoryHUDRenderer', 'HUD Sequence'): ('confirmed', '0x469fa0', QT_TRANSLATE_NOOP(
        'fieldhelp', "HUD sequence drawn as the flag's HUD display at the item's HUD position, played in a loop (synchronised "
        'to the game clock).')),
    ('CFlagInventoryHUDRenderer', 'Animation Speed'): ('confirmed', '0x469fa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Factor on the frame rate of "HUD Sequence" (-10..10); a negative value plays it backwards. Default 1.')),
    ('CWeaponInventoryHUDRenderer', 'Show Ammo Icon'): ('confirmed', '0x485cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 draws the ammunition\'s icon after the "+N" rounds text. This only happens for continuous fire weapons '
        'with at least one whole round; for normal weapons the setting has no effect. Default 0.')),
    ('CInventoryItemBase', 'Definition Index'): ('confirmed', '0x4dd480, 0x4dd580', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The item\'s kind: an entry of the item catalogue ("Inventory/Item Definitions"). Everything else about '
        'the item (category, icon, weapon data, limits, buttons) comes from that definition.')),
    ('CInventoryItem', 'Current Delay'): ('confirmed', '0x42a480, 0x42a450, 0x429ea0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds left until the item can be used again; set to the definition\'s "Reuse '
        'Delay" on use and counted down every frame, the item is ready at 0. A value set in a level only delays '
        'the first use.')),
    ('CInventoryItem', 'Broadcaster'): ('confirmed', '0x42a300', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the item's own message broadcaster; when the item is destroyed it tells its "
        'listeners "Delete". Leave unchanged in a level.')),
    ('CInventoryItem', 'Marked For Deletion'): ('confirmed', '0x424fd0, 0x42a890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 when the item is used up; the inventory removes such items in its next update. '
        'Set in a level, the item disappears right at the start.')),
    ('CInventoryItem', 'Currently Selected'): ('confirmed', '0x42a370, 0x42a380, 0x42a550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: 1 while the item is the current one of its inventory category; the inventory sets '
        'and clears it when the selection changes. Leave unchanged in a level.')),
    ('CContinuousFireWeaponItem', 'Muzzel Flash Entity'): ('confirmed', '0x472c90, 0x472dc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the muzzle flash entity (the definition\'s "Shot Flash") that exists while the '
        'continuous fire weapon fires; it is removed when firing stops. Leave empty in a level.')),
    ('CContinuousFireWeaponItem', 'Gun Owner'): ('confirmed', '0x472c90, 0x472c30, 0x472dc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the part that is firing the continuous fire weapon; firing stops when the weapon '
        'is deselected or its owner reports it is gone. Leave empty in a level.')),
    ('CCountInventoryItem', 'Rounds'): ('confirmed', '0x42a810, 0x42a850, 0x42aff0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How many units this item stands for (ammunition, minerals, stored health items, ...). On pickup they are'
        ' added to an item of the same kind the player already has, at most up to the definition\'s "Generate/Max '
        'Count" when that is set; using units takes them away and the item is removed at 0. Default 40 (1 for '
        'health items).')),
    ('CCountInventoryItem', 'Max Rounds'): ('confirmed', '0x5b7490, 0x42a820', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only read on the "Default Inventory Item" of an item definition: after loading, a value other than 0 '
        'becomes the definition\'s "Generate/Max Count" (-1 = unlimited) and is then reset to 0. On items placed '
        'in a level it has no effect.')),
    ('CCountInventoryItem', 'Pickup If Full'): ('confirmed', '0x42adb0, 0x5af390', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 lets the item be picked up even when the player's item of that kind is already at its limit; the "
        'rounds beyond the limit are lost. For a health item: picked up even at full health. Default 0.')),
    ('CHealthItem', 'Num Health'): ('confirmed', '0x5af3e0, 0x4dd220, 0x5b83c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Hit points healed when the item is used or picked up (not stored), at most up to the character's full "
        'hit points (1..200). Default 10. Fruit also count by this value for the quest statistics.')),
    ('CHealthItem', 'Storable Item'): ('confirmed', '0x5af3e0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: on pickup the item goes into the inventory (stacked by "Rounds") to be used later; 0: it heals right '
        'away when picked up. Default 0.')),
    ('CDeployedInventoryItem', 'Deployed Entity'): ('confirmed', '0x47a0f0, 0x47a990, 0x47a8d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the entity this deployed item put into the level (e.g. a placed turret); recalling'
        ' the item removes it. Leave empty in a level.')),
    ('CDeployedInventoryItem', 'Owner'): ('confirmed', '0x47a0f0, 0x47a8d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the character that deployed the entity; when the owner leaves the scope the entity'
        ' is recalled. Leave empty in a level.')),
    ('CUndeployedInventoryItem', 'Current Damage'): ('confirmed', '0x47a0f0, 0x47a990, 0x479e00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage the deployable already has: when it is deployed, the entity loses this many hit points '
        "(unavoidable damage); recalling stores the entity's lost hit points here. A value in a level makes the "
        'deployed entity start damaged.')),
    ('CEnergyItem', 'Current Charge'): ('confirmed', '0x5afe50, 0x5afe60, 0x5afe90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The item\'s charge in mega-joules. Gaining charge stops at the definition\'s "Energy"; a value set in a '
        "level is not capped. For energy pickups it is the amount added to the player's item of that kind.")),
    ('CCharacterInventoryItem', 'Special Ability Level'): ('confirmed', '0x580070, 0x580bd0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Current level of the special ability, counted from 0 (shown +1); selects the entry of the definition's "
        '"Special/Level" list for charge time, duration and actions. It rises when the character collects enough '
        'of the category\'s "Advance/Item Needed To Advance".')),
    ('CCharacterInventoryItem', 'Is Discharging'): ('confirmed', '0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: 1 while the special ability is active; the charge then runs down over the level's "
        '"Duration", and when it is empty the ability stops and the level\'s "Deactivate Action" runs. Otherwise '
        'the item recharges over "Charge Time".')),
    ('CEnergyStorageItem', 'Pickup If Full'): ('confirmed', '0x5b0250, 0x5b02c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 lets the item be picked up even when the player's item of the same class is full, or when the player "
        'has none; the charge that does not fit is lost. 0: only picked up while that item is below its "Energy".'
        ' Default 0.')),
    ('CShieldInventoryItem', 'Damage Type'): ('confirmed', '0x56e410, 0x56e3b0, 0x56da70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The damage type this shield blocks. A character keeps one shield per type: a new shield of the same type'
        ' is only taken when its definition\'s "Energy" is higher, and then replaces the old one.')),
    ('CShieldInventoryItem', 'Shield Gfx'): ('confirmed', '0x56d960, 0x56da70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model of the shield effect: on the first hit it is created as a child of the character, turned towards '
        'the hit point and played on every absorbed hit.')),
    ('CShieldInventoryItem', 'AI'): ('confirmed', '0x56e520, 0x56da70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The shield AI (a CShieldAI) given to the character on pickup, unless it already has one for this damage '
        'type; that AI absorbs the damage while the item has charge.')),
    ('CSphereOfZinEnergyInventoryItem', 'Charge Last Update'): ('confirmed', '0x584960, 0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: the charge at the previous update; the Sphere of Zin's thresholds fire when the "
        'charge crossed them between this value and the current one. Leave unchanged.')),
    ('CSphereOfZinEnergyInventoryItem', 'Charge Next Update'): ('confirmed', '0x584d40, 0x584960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the charge collected for the next update (evil broadcast nearby adds to it, at '
        'most the most charge); it becomes the current charge at the next step. Leave unchanged.')),
    ('CSphereOfZinEnergyInventoryItem', 'List of ReTriggerable Thresholds'): ('confirmed', '0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: one armed flag per threshold of the Sphere of Zin data; a threshold fires once, '
        'then re-arms when the charge has moved its margin away from it. Leave unchanged.')),
    ('CSegmentedInventoryItem', 'Segments'): ('confirmed', '0x5698a0, 0x569b70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The pieces (segment entries) this item brings. On pickup the pieces the assembled item needs are added '
        "to the player's segmented item; when all are there, the definition's completed item is given and its "
        'action runs.')),
    ('CInventoryItemDefinition', 'Icon Image'): ('confirmed', '0x4da290, 0x502b10, 0x4d68a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Image from "Inventory Icons" shown for the item in the inventory screen\'s item list and in the materials'
        " generator's list.")),
    ('CInventoryItemDefinition', 'Generator Icon Image'): ('confirmed', '0x502b10, 0x4d6b70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Small image from "Inventory Icons" shown when this item is an ingredient in the materials generator\'s '
        "cost column, and next to the icon in the item's detail display.")),
    ('CInventoryItemDefinition', 'Inventory Type'): ('confirmed', '0x4dd580, 0x5b7af0, 0x5b7490', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The item\'s category ("Inventory/Item Types", e.g. Primary, Secondary, Health, Shield). It decides the '
        'HUD position and renderer, which items replace each other as the current one, and the use action set up '
        'after loading.')),
    ('CInventoryItemDefinition', 'Default Inventory Item'): ('confirmed', '0x5b7490, 0x503960, 0x42a550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Template item of this kind: cloned when the item is given by a default give action, made in the '
        'materials generator or brought as ammunition with a weapon; a count item\'s "Max Rounds" here sets '
        '"Generate/Max Count".')),
    ('CInventoryItemDefinition', 'Shot Flash'): ('confirmed', '0x4c4ee0, 0x472c90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model spawned at the muzzle when the weapon fires (an explosion-type effect); for a continuous fire '
        'weapon it stays as a child of the shooter while firing.')),
    ('CInventoryItemDefinition', 'Ammunition'): ('confirmed', '0x4d77c0, 0x5aeec0, 0x42a550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Item kind the weapon uses as ammunition. With it, firing needs and uses "Rounds Needed" rounds of that '
        'item; without it the weapon uses battery energy. Picking up the weapon also brings one item of its '
        'ammunition.')),
    ('CInventoryItemDefinition', 'Max Shoot Angle'): ('confirmed', '0x4d6520, 0x578240, 0x578460', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Aiming tolerance in degrees (0..180): a computer-controlled character only fires this weapon when its '
        'target lies within this angle of its aiming direction; it is also drawn as the aiming cone in debug '
        'view. Default 10.')),
    ('CInventoryItemDefinition', 'Strike Damage'): ('confirmed', '0x4d6530, 0x4c4e00, 0x5b79f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Melee damage: above 0 the weapon strikes instead of firing projectiles, damaging everything within '
        '"Strike Damage Radius" around the muzzle point. For continuous fire weapons it is the beam\'s damage. '
        'Default 0.')),
    ('CInventoryItemDefinition', 'Strike Damage Type'): ('confirmed', '0x4c4e00', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage type of the strike ("Strike Damage").')),
    ('CInventoryItemDefinition', 'Strike Damage Radius'): ('confirmed', '0x4c4e00, 0x5b79f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Radius in pixels of the strike's damage around the muzzle point. For continuous fire weapons it is the "
        "beam's range; the extra close range damage falls off to 0 at this distance. Default 10.")),
    ('CInventoryItemDefinition', 'Discharge Sequence'): ('confirmed', '0x4d6540, 0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence the shooter plays when firing. A character turned sideways uses "ShootLeft"/"ShootRight" '
        'instead when its model has them. Default "Shoot1".')),
    ('CInventoryItemDefinition', 'Energy'): ('confirmed', '0x5afe50, 0x5b8010, 0x5a7e80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Energy in mega-joules. For energy items (batteries, shields, special abilities) it is the most charge; '
        'shields of one type are compared by it. For a weapon without ammunition a negative value is the battery '
        'charge each shot needs and uses (scaled by the world settings for the player).')),
    ('CInventoryItemDefinition', 'Rounds Needed'): ('confirmed', '0x5b8010, 0x5a7e80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Rounds of the "Ammunition" item a shot needs and uses up; with fewer the weapon cannot fire. Default 1.')),
    ('CInventoryItemDefinition', 'New Shot Action'): ('confirmed', '0x4c4ee0, 0x5ab9a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run for every fired projectile, with the projectile as trigger (e.g. a mine playing its "Deploy" '
        'sequence).')),
    ('CInventoryItemDefinition', 'Shot Sound'): ('confirmed', '0x4c5270', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played at the shooter after the weapon fired. "!None.wav": none.')),
    ('CInventoryItemDefinition', 'Projectile'): ('confirmed', '0x4c4ee0, 0x5b8010, 0x47a0f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model fired by the weapon; its entity must be a projectile (CEntityProjectile), else the shot fails with'
        ' an error. A weapon without a projectile cannot be used as a weapon. Deployables and mines create this '
        'model.')),
    ('CInventoryItemDefinition', 'Num Projectile'): ('confirmed', '0x4c5270, 0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Projectiles per shot: one entry per projectile with its spread angle (degrees) and X/Y offset from the '
        'muzzle. Empty: one projectile straight ahead.')),
    ('CInventoryItemDefinition', 'Reuse Delay'): ('confirmed', '0x42a480, 0x429ea0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds after a use before the item can be used again (the fire rate of a weapon). Default 0.3.')),
    ('CZaxInventoryItemDefinition', 'Place Button'): ('confirmed', '0x4db430, 0x4db630', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 shows a "Place" button on the inventory screen while this item is in focus; clicking it runs "Place '
        'Button Action" for the player.')),
    ('CZaxInventoryItemDefinition', 'Place Button Label'): ('confirmed', '0x5b76e0, 0x4db430', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the "Place" button (a Local.txt entry); empty uses the default "&Place".')),
    ('CZaxInventoryItemDefinition', 'Place Button Action'): ('confirmed', '0x4db630', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run for the player when the "Place" button is clicked; if it fails an error sound plays.')),
    ('CZaxInventoryItemDefinition', 'Disable Button'): ('confirmed', '0x4db430, 0x4db630', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 shows a "Disable" button on the inventory screen while this item is in focus; clicking it runs '
        '"Disable Button Action".')),
    ('CZaxInventoryItemDefinition', 'Disable Button Label'): ('confirmed', '0x5b7710, 0x4db430', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the "Disable" button (a Local.txt entry); empty uses the default "D&isable".')),
    ('CZaxInventoryItemDefinition', 'Disable Button Action'): ('confirmed', '0x4db630', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run for the player when the "Disable" button is clicked; if it fails an error sound plays.')),
    ('CZaxInventoryItemDefinition', 'Use Button'): ('confirmed', '0x4db430, 0x4db630, 0x5b7490', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 shows a "Use" button on the inventory screen while this item is in focus. For items of the categories '
        'Health, Primary and Secondary the game sets up the use action itself after loading (heal, or select the '
        'weapon).')),
    ('CZaxInventoryItemDefinition', 'Use Button Label'): ('confirmed', '0x5b7740, 0x4db430', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the "Use" button (a Local.txt entry); empty uses the default "&Use".')),
    ('CZaxInventoryItemDefinition', 'Use Button Action'): ('confirmed', '0x4db630, 0x5b7490', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run for the player when the "Use" button is clicked. An old generic item action here is replaced '
        'after loading by the category\'s own use action (Health: heal, Primary/Secondary: select) when "Use '
        'Button" is set.')),
    ('CZaxInventoryItemDefinition', 'Undefined'): ('confirmed', '0x4db430, 0x4db630', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 shows a fourth, freely usable button on the inventory screen while this item is in focus; clicking it '
        'runs "Undefined Button Action".')),
    ('CZaxInventoryItemDefinition', 'Undefined Button Label'): ('confirmed', '0x5b7770, 0x4db430', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the fourth button (a Local.txt entry); empty uses the default label "Undefined".')),
    ('CZaxInventoryItemDefinition', 'Undefined Button Action'): ('confirmed', '0x4db630', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run for the player when the fourth button is clicked; if it fails an error sound plays.')),
    ('CZaxInventoryItemDefinition', 'PowerUp Model'): ('confirmed', '0x4dc590, 0x5b76d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model of the pickup created when the player drops this item; it gets a pickup AI holding the dropped '
        'item.')),
    ('CZaxInventoryItemDefinition', 'Ingredient 1 Quantity'): ('confirmed', '0x5034f0, 0x503960, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How many of "Ingredient 1 Type" the materials generator needs to make this item; they are used up. 0 (or'
        ' no type): this ingredient is not needed. An item without any ingredient is not offered by the '
        'generator.')),
    ('CZaxInventoryItemDefinition', 'Ingredient 1 Type'): ('confirmed', '0x5034f0, 0x503960, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Mineral item (e.g. ore or crystals) used as ingredient 1 in the materials generator; its "Generator Icon'
        ' Image" and name are shown in the cost column.')),
    ('CZaxInventoryItemDefinition', 'Ingredient 2 Quantity'): ('confirmed', '0x5034f0, 0x503960, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How many of "Ingredient 2 Type" the materials generator needs to make this item; they are used up. 0 (or'
        ' no type): this ingredient is not needed. An item without any ingredient is not offered by the '
        'generator.')),
    ('CZaxInventoryItemDefinition', 'Ingredient 2 Type'): ('confirmed', '0x5034f0, 0x503960, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Mineral item (e.g. ore or crystals) used as ingredient 2 in the materials generator; its "Generator Icon'
        ' Image" and name are shown in the cost column.')),
    ('CZaxInventoryItemDefinition', 'Ingredient 3 Quantity'): ('confirmed', '0x5034f0, 0x503960, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How many of "Ingredient 3 Type" the materials generator needs to make this item; they are used up. 0 (or'
        ' no type): this ingredient is not needed. An item without any ingredient is not offered by the '
        'generator.')),
    ('CZaxInventoryItemDefinition', 'Ingredient 3 Type'): ('confirmed', '0x5034f0, 0x503960, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Mineral item (e.g. ore or crystals) used as ingredient 3 in the materials generator; its "Generator Icon'
        ' Image" and name are shown in the cost column.')),
    ('CZaxInventoryItemDefinition', 'Must be discovered fist'): ('confirmed', '0x5034f0, 0x5a6390', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the materials generator only offers this item after the player has discovered it (an inventory '
        'discover action). Default 0.')),
    ('CZaxInventoryItemDefinition', 'HUD Renderer'): ('confirmed', '0x5b7f00, 0x59e730, 0x5b7ab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Renderer that draws the item in the HUD (compass, weapon ammo, energy meter, flag, ...). Empty: the '
        'category\'s "Default HUD Renderer" is used.')),
    ('CZaxInventoryItemDefinition', 'Detail Renderer'): ('confirmed', '0x5b7a60, 0x5b7e20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Renderer for the item's detail text and pictures on the inventory screen and its line in the item list "
        '(e.g. ammunition count, charge, segments needed). Empty: a plain "Qty" line.')),
    ('CZaxInventoryItemDefinition', 'Detail Image'): ('confirmed', '0x5b80d0, 0x5b9110, 0x5adea0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Large picture (detail sequence) shown for the item on the inventory screen.')),
    ('CZaxInventoryItemDefinition', 'HUD Image'): ('confirmed', '0x5acab0, 0x5b9110', QT_TRANSLATE_NOOP(
        'fieldhelp', "Icon (first frame of a HUD sequence) drawn for the item in the HUD at its category's HUD position, and "
        'right of the detail image on the inventory screen.')),
    ('CZaxInventoryItemDefinition', 'InventoryItem Specific Data'): ('confirmed', '0x5b7640, 0x5b79f0, 0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Extra data object of special items: continuous fire weapon data (start/finish actions, impact explosion,'
        ' spread, close range damage, looping sound) makes the weapon a continuous fire weapon; Sphere of Zin '
        'data holds its charge thresholds.')),
    ('CZaxInventoryItemDefinition', 'Switch Inventory Sound'): ('confirmed', '0x5b7c50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when the player switches to this item. "!None.wav": the category\'s "Default Inventory '
        'Select Sound" is used.')),
    ('CZaxInventoryItemDefinition', 'Max Count'): ('confirmed', '0x5b83c0, 0x42afa0, 0x5b7490', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Most units of this item kind a character can carry; further pickups are refused and stacks are capped. '
        '0: unlimited. Overwritten after loading by a non-zero "Max Rounds" of the default item.')),
    ('CZaxInventoryItemDefinition', 'Required Item'): ('confirmed', '0x5b83c0, 0x5b88f0, 0x5034f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The lesser item this one upgrades: the materials generator only offers this item while the player has '
        'the required one and uses it up; getting this item removes the required chain, and while the player has '
        'it, items of that chain are no longer picked up.')),
    ('CZaxInventoryItemDefinition', 'Item Priority'): ('confirmed', '0x5b8b00, 0x42a3b0, 0x425a70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A higher value wins: when an item is picked up, it becomes the current one of its category if its '
        "priority is higher than the current item's (ties go by catalogue order), which also drives the automatic"
        ' weapon switch.')),
    ('CEnergyItemDefinition', 'Energy Meter'): ('confirmed', '0x486d10, 0x581d20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Colours of the item's energy meter (line and charged colours, dim and bright). A meter taller than wide "
        'is drawn black with a border and filled from the bottom; a wider one as a bar filled from the left.')),
    ('CEnergyItemDefinition', 'Spacing'): ('confirmed', '0x56f280', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Meant as the vertical gap between shield meters, but the shield HUD overwrites the position for every '
        'shield, so the value has no effect. Default 10.')),
    ('CEnergyItemDefinition', 'Width'): ('confirmed', '0x581d20, 0x56f280', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width of the energy meter in the HUD in pixels, centred on the item's HUD position. Default 50.")),
    ('CEnergyItemDefinition', 'Height'): ('confirmed', '0x581d20, 0x56f280, 0x486d10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height of the energy meter in the HUD in pixels; when it is larger than the width the meter is vertical.'
        ' Default 10.')),
    ('CCharacterInventoryItemDefinition', 'Special Ability'): ('confirmed', '0x582270, 0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Which special ability this character item gives; its name is shown in the HUD and in the level-up '
        'message.')),
    ('CCharacterInventoryItemDefinition', 'Level'): ('confirmed', '0x580070, 0x580bd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The ability\'s levels in order, each with description, "Charge Time" (seconds to charge fully), '
        '"Duration" (seconds of use), activate sound and activate/deactivate actions.')),
    ('CInventoryItemHolder', 'The Item'): ('confirmed', '0x424da0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only for old level files: an inventory\'s legacy "Inventory Holders" block wraps each item in such a '
        'holder, and the item is moved into the inventory when loading.')),
    ('CZaxInventoryTypeDefinition', 'X HUD Position'): ('confirmed', '0x4298d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal HUD position in pixels of this category\'s current item, measured from the edge chosen by "X '
        'HUD Screen Justify" (from the left, from the centre, or inwards from the right edge).')),
    ('CZaxInventoryTypeDefinition', 'X HUD Screen Justify'): ('confirmed', '0x4298d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Reference for "X HUD Position": Left (from the left edge), Center (from the screen centre) or Right (the'
        ' position counts leftwards from the right edge).')),
    ('CZaxInventoryTypeDefinition', 'Y HUD Position'): ('confirmed', '0x4298d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Vertical HUD position in pixels of this category\'s current item, measured from the edge chosen by "Y HUD'
        ' Screen Justify".')),
    ('CZaxInventoryTypeDefinition', 'Y HUD Screen Justify'): ('confirmed', '0x4298d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Reference for "Y HUD Position": Top (from the top edge), Center (from the screen centre) or Bottom (the '
        'position counts upwards from the bottom edge).')),
    ('CZaxInventoryTypeDefinition', 'Render In HUD'): ('confirmed', '0x429ae0, 0x429980', QT_TRANSLATE_NOOP(
        'fieldhelp', '1: the current item of this category (both items while switching, cross-faded) is drawn in the HUD. 0: '
        'the category does not appear in the HUD.')),
    ('CZaxInventoryTypeDefinition', 'Render In Editor'): ('confirmed', '0x429ae0, 0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Selects the categories for a second HUD record pass, but the game only ever runs the normal pass, so the'
        ' switch has no effect in the game.')),
    ('CZaxInventoryTypeDefinition', 'Lock to Inventory Bar'): ('confirmed', '0x4298d0, 0x429880', QT_TRANSLATE_NOOP(
        'fieldhelp', "1: the HUD position moves up with the inventory bar as it slides in (the bar's shown height is "
        'subtracted from Y), so the display stays on top of the bar.')),
    ('CZaxInventoryTypeDefinition', 'Sort Priority'): ('confirmed', '0x5b29a0, 0x5b2aa0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Order of the categories in the inventory's item list and statistics: categories with a higher value come"
        ' first.')),
    ('CZaxInventoryTypeDefinition', 'Default HUD Renderer'): ('confirmed', '0x5b7f00, 0x59e730', QT_TRANSLATE_NOOP(
        'fieldhelp', 'HUD renderer for items of this category whose definition has no "Display/HUD Renderer" of its own. '
        'Without either, the item is not drawn in the HUD.')),
    ('CZaxInventoryTypeDefinition', 'Default Inventory Select Sound'): ('confirmed', '0x5b7c50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when the player switches to an item of this category whose own "Switch Inventory Sound" is '
        '"!None.wav". "!None.wav" here: silent.')),
    ('CCharacterInventoryTypeDefinition', 'Item Needed To Advance'): ('confirmed', '0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', "Item kind the character must collect to raise its special ability's level; the needed amount is used up "
        'on each level-up.')),
    ('CCharacterInventoryTypeDefinition', 'Level'): ('confirmed', '0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of "Item Needed To Advance" required for each level-up, in order (entry 0: from the first to the '
        'second level). An entry of 0 or the end of the list stops advancing.')),
    ('CItemTypeData', 'Seconds Into Change'): ('confirmed', '0x424fd0, 0x425590, 0x429980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of an inventory category: seconds since the switch to another item started; the '
        'switch finishes when it reaches "Seconds To Change". Leave unchanged in a level.')),
    ('CItemTypeData', 'Seconds To Change'): ('confirmed', '0x425590, 0x424fd0, 0x429980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: length of the current item switch in seconds (0.33 when the player cycles weapons '
        'by key, else 0); the HUD cross-fades the two items over this time. Leave unchanged in a level.')),
    ('CItemTypeData', 'Cur Inventory Index'): ('confirmed', '0x424fd0, 0x425590', QT_TRANSLATE_NOOP(
        'fieldhelp', "Position in the inventory's item list of this category's current item (-1: none selected). With -1 the "
        "inventory selects the category's first item at its first update; a valid index set in a level makes that"
        ' item the current one.')),
    ('CItemTypeData', 'Changing To Inventory Index'): ('confirmed', '0x424fd0, 0x425590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: position of the item this category is switching to (-1: not changing); it becomes '
        'the current item when the switch time is over. Leave at -1 in a level.')),
    ('CZaxLayerSaveData', 'Compass Target'): ('confirmed', '0x423e90, 0x5a44b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the object the compass points to in this layer; at the start the compass looks it up by name (no'
        ' match: no target). Set by the set-compass-target action; empty: no target.')),
    ('CLayerHolder', 'UniqueID'): ('confirmed', '0x4efe20, 0x4f4e70, 0x5a0e70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of a game: a random non-zero ID drawn at the start of a new game; when a save game '
        'with another ID is loaded, the playing time counter starts again. Leave unchanged.')),
    ('CLayerHolder', 'Total Playing Time Up To Last Save'): ('confirmed', '0x4efe90, 0x5a0c80, 0x4f2610', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: playing time in seconds accumulated up to the last save; the time of the current '
        'mission is added on saving. Shown as the total playing time. Leave unchanged.')),
    ('CLayerHolder', 'Simulation Running Time'): ('confirmed', '0x4f3560, 0x4f2600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: seconds the game simulation has run, advanced every unpaused frame. Leave '
        'unchanged.')),
    ('CLayerPart', 'Name'): ('confirmed', '0x4fbf20, 0x57aa80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the object. Actions, triggers and AIs find their targets by this name (comma lists and #a-b# '
        "ranges in their name fields); it is also the object's display name. Several objects may share a name.")),
    ('CLayerPart', 'Child List'): ('confirmed', '0x4fadc0, 0x4fa9a0, 0x4fafa0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Owned list of child objects attached to this one (e.g. an attachment of an entity). Children are updated'
        ' with the parent, drawn and sent messages while they are visible, and their position counts relative to '
        "the parent's position.")),
    ('CLayerPart', 'Visible'): ('confirmed', '0x488d70, 0x4fa9a0, 0x4fb880', QT_TRANSLATE_NOOP(
        'fieldhelp', '0/1 (default 1): the object is drawn only while Visible and Active are both set. Invisible children also'
        ' get no draw pass and no messages from their parent. Collision is not affected.')),
    ('CLayerPart', 'Collideable'): ('verified', '0x4e8e00, 0x4fa930, 0x4c1c60', QT_TRANSLATE_NOOP(
        'fieldhelp', '0/1 (default 1): an active object with this flag is an obstacle in every collision sweep (walking, '
        "projectiles, line of sight); its polygon or the model's bounds polygon is the shape. A surface or "
        'polygon without it can be walked through.')),
    ('CLayerPart', 'Half Height'): ('confirmed', '0x4fa900, 0x4e8e00', QT_TRANSLATE_NOOP(
        'fieldhelp', '0/1: a low obstacle. Setting it clears Full Height (the two exclude each other), so shots and '
        'line-of-sight checks pass over the object while it still blocks walking. The flag itself is only asked '
        'for by sweeps of kind 1, which no game code was found to use.')),
    ('CLayerPart', 'Full Height'): ('confirmed', '0x4fa970, 0x4e8e00, 0x492060, 0x491380', QT_TRANSLATE_NOOP(
        'fieldhelp', '0/1 (default 1): a full-height obstacle. Only collideable objects with this flag stop projectiles and '
        'block line of sight (AIs seeing targets, turret aiming, beam weapons); without it the object only blocks'
        ' walking. Setting it clears Half Height.')),
    ('CLayerPart', 'Tries To Collide'): ('confirmed', '0x491160, 0x537d40, 0x5383f0', QT_TRANSLATE_NOOP(
        'fieldhelp', '0/1: a moving entity with this flag moves through the collision sweep and is stopped or bounced by '
        'obstacles (and tells what it hits); without it the entity is placed at its new position directly, '
        'through walls. Objects with it are also ignored as obstacles when the way-point map is built, and a '
        'way-point polygon with it is left out.')),
    ('CLayerPart', 'Has Hit Points'): ('confirmed', '0x48d6f0, 0x48d380, 0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: set when a destructable object is activated with hit points left and cleared when it '
        'dies. Beam weapons only damage targets with it, AI target searches can require it, and objects with it '
        'do not block way points. Recomputed for destructables; leave unchanged in a level.')),
    ('CLayerPart', 'Stationary'): ('verified', '0x490fc0, 0x491160, 0x488d70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state saved as 1 for every object of the original levels: the object rests. Resting objects are'
        ' not redrawn every frame (resting ground parts stay in the cached ground) and movable entities do not '
        'move or apply velocity; behaviours clear the flag while they animate or move and set it again '
        'afterwards, and non-animated entities get it after every drawing.')),
    ('CLayerPart', 'Active'): ('verified', '0x4fadc0, 0x4fb540, 0x4fac20, 0x4e71b0', QT_TRANSLATE_NOOP(
        'fieldhelp', '0/1 (default 1): an inactive object is not updated, not drawn, does not collide and cannot be shot; its '
        'AIs do not run. Switching it on (e.g. by an activate action) runs the activation: the AIs begin and the '
        'object gets the "Begin" message; switching off sends "End".')),
    ('CLayerPart', 'Is Temporarily Excluded'): ('confirmed', '0x4e8e00, 0x4912b0, 0x491380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: while set, the object is skipped by every collision sweep. The game sets it for a moment'
        ' during line-of-sight, free-path and blocker tests and restores it afterwards; leave unchanged in a '
        'level (set, the object would never collide).')),
    ('CLayerPart', 'Is Marked For Deletion'): ('confirmed', '0x4fadc0, 0x4fbf30, 0x4face0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the object has died or was removed and is deleted at the next update of its parent or '
        'layer; it is not drawn any more. Leave unchanged in a level (set, the object disappears at once).')),
    ('CLayerPart', 'Activity'): ('confirmed', '0x4fac20, 0x4fadc0, 0x4fb880', QT_TRANSLATE_NOOP(
        'fieldhelp', "The object's own AIs (triggers, behaviours, scripted logic). They begin when the object is activated, "
        'are updated every frame while it is active and receive its messages and collisions; an AI that reports '
        "itself done is removed and deleted. Entities also run the AIs of their model's Activity first.")),
    ('CLayerPart', 'Category'): ('confirmed', '0x48d380, 0x49b090, 0x4ed2b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Category names (from the game's Categories definitions); each is stored as a bit of the object's flag "
        'word (bit = index in the sorted list). AIs use them to choose targets and partners (e.g. Valid Targets, '
        "Collides with, Who Can Pick Up); the Player and Enemy categories select the difficulty's damage factor, "
        'and NonInteractiveSequence Actor characters keep acting during non-interactive sequences.')),
    ('CLayerPart', 'Team Number'): ('confirmed', '0x4fa960, 0x4f4950, 0x544cf0', QT_TRANSLATE_NOOP(
        'fieldhelp', '0-15, or -1 "Nutral" (default). Used by the team actions (Is On Team, Is On Same Team, Give My Team A '
        'Point), by the friendly-fire test of player characters (projectiles of the same team do not hit unless '
        "the game type allows it) and as the index into the level's Team Info when a character is placed without "
        'a spawn point name (-1 uses team 0).')),
    ('CLayerPart', 'Used In'): ('confirmed', '0x57a6e0, 0x4ed5c0, 0x4f4890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Game types the object exists in (default $All). When a level starts, every object whose Used In lacks '
        'the current game type is removed (it "dies" and is deleted), so this splits quest and multiplayer '
        'content in one map.')),
    ('CLayerPart', 'Current Target'): ('confirmed', '0x4fc2e0, 0x4fc270, 0x4fc260', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the object this one currently targets and listens to (set by AIs); it is forgotten when '
        'the target dies, is deleted or leaves scope. Leave unchanged in a level.')),
    ('CLayerPart', 'Broadcaster'): ('confirmed', '0x4fc1b0, 0x4fbf30, 0x4fc240', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the list of objects listening to this one (created by the first listener); it sends them'
        ' messages such as "Died" and "Delete". Leave unchanged in a level.')),
    ('CEntityBase', 'Model'): ('confirmed', '0x48b390, 0x48f4b0, 0x48b860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The model (Cache/Models/<name>.mdl16) that gives the entity its graphics, sequences, bounds polygon, hit'
        " points and model AIs. Changing it re-lists the object and starts with the model's first sequence "
        '(animated entities: its default sequence, frame 0, movement angle 0).')),
    ('CEntityBase', 'Position X'): ('confirmed', '0x48a0a0, 0x489fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'World x coordinate in pixels (decimals allowed). Setting it moves the object, rounds the integer '
        "position and re-lists it in the layer's grid.")),
    ('CEntityBase', 'Position Y'): ('confirmed', '0x48a0d0, 0x489fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'World y coordinate in pixels (decimals allowed); the ground point of the object, which also decides its '
        "drawing order. Setting it moves the object and re-lists it in the layer's grid.")),
    ('CEntityBase', 'Rendering Height'): ('confirmed', '0x48b6b0, 0x488d70, 0x4c6e30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height above the ground in pixels (-500..500): the object is drawn that many pixels higher while its '
        'collision and sorting point stay on the ground. Setting it also sets Rendering Height Float.')),
    ('CEntityBase', 'Rendering Height Float'): ('confirmed', '0x48b770, 0x490fc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The same height as a float (-500..500 pixels); movable entities change it through their height velocity.'
        ' A change of 0.01 or less is ignored; the integer Rendering Height is its rounded value.')),
    ('CEntityBase', 'Cur Sequence'): ('confirmed', '0x48b120, 0x48f700, 0x48b590', QT_TRANSLATE_NOOP(
        'fieldhelp', "The model's sequence the entity shows now (by name; none = -1). AIs and behaviours change it while "
        'playing; in a level it sets the starting animation or pose.')),
    ('CEntityAnimatedLine', 'BoundLeft'): ('confirmed', '0x493850, 0x4931b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state: the left edge (world pixels) of the rectangle around the line's drawing strips, "
        "recomputed whenever the line is set; used as the object's rectangle (raised by the rendering height). No"
        ' original level uses this class.')),
    ('CEntityAnimatedLine', 'BoundTop'): ('confirmed', '0x493850, 0x4931b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state: the top edge (world pixels) of the rectangle around the line's drawing strips, "
        "recomputed whenever the line is set; used as the object's rectangle (raised by the rendering height). No"
        ' original level uses this class.')),
    ('CEntityAnimatedLine', 'BoundRight'): ('confirmed', '0x493850, 0x4931b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state: the right edge (world pixels) of the rectangle around the line's drawing strips, "
        "recomputed whenever the line is set; used as the object's rectangle (raised by the rendering height). No"
        ' original level uses this class.')),
    ('CEntityAnimatedLine', 'BoundBottom'): ('confirmed', '0x493850, 0x4931b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state: the bottom edge (world pixels) of the rectangle around the line's drawing strips, "
        "recomputed whenever the line is set; used as the object's rectangle (raised by the rendering height). No"
        ' original level uses this class.')),
    ('CEntityAnimatedLine', 'Outside Color'): ('confirmed', '0x4923e0, 0x4936b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Colour of the two outer lines drawn on both sides of the line (default 205, 20, 25, 255).')),
    ('CEntityAnimatedLine', 'Middle Color'): ('confirmed', '0x4923e0, 0x4936b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Colour of the centre line (default 255, 200, 25, 255).')),
    ('CEntityAnimatedLine', 'Start'): ('confirmed', '0x493520, 0x493850', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Start point of the line (world pixels); the code makes the end point with the smaller y the start and '
        'moves the object there. The drawing strips are built only when the line is set by the game (or a network'
        ' update); they are not saved, so editing the point alone does not rebuild them.')),
    ('CEntityAnimatedLine', 'End'): ('confirmed', '0x493520, 0x493850', QT_TRANSLATE_NOOP(
        'fieldhelp', 'End point of the line (world pixels). Like Start it only takes effect when the line is set by the game, '
        'which rebuilds the strips.')),
    ('CEntityAnimatedLine', 'Normal'): ('confirmed', '0x493520', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: unit direction from start to end ((1, 0) for equal points), recomputed when the line is '
        'set.')),
    ('CEntityAnimatedLine', 'PerpenNormal'): ('confirmed', '0x493520, 0x4923e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: unit vector perpendicular to the line, recomputed when the line is set; the outer lines '
        'are drawn offset by it.')),
    ('CEntityAnimatedLine', 'Width'): ('confirmed', '0x493850, 0x492f50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the band around the line that the drawing strips cover (new lines get 4); it sets the'
        " strips' extent and the bounds, the lines themselves are drawn one pixel apart.")),
    ('CEntityDestructable', 'Cur Damage'): ('confirmed', '0x48d380, 0x48d030, 0x48d330', QT_TRANSLATE_NOOP(
        'fieldhelp', "Damage taken so far, in hit points; the remaining hit points are the model's hit points minus this (at "
        "least 0). A value in the level starts the object damaged; at or above the model's hit points it counts "
        'as dead and takes no more damage. Healing lowers it.')),
    ('CEntityDestructable', 'Destroyed Action'): ('confirmed', '0x48d380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run once when the damage reaches the hit points, before the object dies (death type, "Died" '
        'message); the damage dealer is passed along.')),
    ('CEntityDestructable', 'Damaged Action'): ('confirmed', '0x48d380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run on every hit that still does damage after all modifiers (difficulty factor, AIs), before the '
        'damage is added.')),
    ('CEntityDestructable', 'Hit Action'): ('confirmed', '0x48d380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run on every damage call on a living object, before the modifiers are applied, even if the hit '
        'ends up doing no damage.')),
    ('CEntityDestructable', 'Default Death Type'): ('confirmed', '0x48cdf0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Death behaviour used when the object dies (from the Death Behaviors list). With the game's default type "
        'the object is simply marked for deletion; any other type runs that death behaviour (e.g. a corpse or '
        'debris). An AI of the class CBehaviorActivity can take over the death instead.')),
    ('CEntityAnimated', 'Play Ratio'): ('confirmed', '0x48f6a0, 0x48f700, 0x4990e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Speed factor of the animation: the sequence's frames per second are multiplied by it (0 = frozen, 1 = "
        'normal, negative = backwards; facing backwards negates it). Behaviours and AIs set it while they play; '
        'values outside -10..10 give a warning. New entities start with 0.')),
    ('CEntityAnimated', 'Aiming Angle'): ('confirmed', '0x48e8f0, 0x48f8b0, 0x48f300', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: direction of the upper body or weapon in radians (0..2π, shown in degrees). Without an '
        "upper body it follows the movement angle. Note: the field's setter is the same as Movement Angle's, so a"
        ' value typed here turns the movement angle and sets Start FacingAngle instead.')),
    ('CEntityAnimated', 'Movement Angle'): ('confirmed', '0x48e8f0, 0x48fa00, 0x48fc50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Direction the entity faces and moves, in radians (0..2π, shown in degrees); it picks the rotation of the'
        ' sequence. Setting it also turns attached animated children and stores the value as Start FacingAngle.')),
    ('CEntityAnimated', 'Start FacingAngle'): ('confirmed', '0x48e8f0, 0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The facing angle the entity had when placed (radians), written whenever Movement Angle is set in the '
        'editor or level. CChaseInvestigateAI turns the entity back to it after a chase.')),
    ('CEntityAnimated', 'Current Frame'): ('confirmed', '0x48feb0, 0x48e9b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: position in the current sequence in frames (a float; the frame shown is its integer '
        "part). Setting it wraps the value into the sequence's length. In a level it gives the starting frame.")),
    ('CEntityAnimated', 'Created By'): ('confirmed', '0x48f1a0, 0x48f1e0, 0x48cb90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the object that created this one (e.g. the shooter of a projectile or the layer of a '
        'mine). Damage and kills it causes are credited to that creator; it is forgotten when the creator dies or'
        ' is deleted.')),
    ('CEntityAnimated', 'BehaviorStack'): ('confirmed', '0x49a480, 0x49a6b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the stack of small behaviours (turn, move, play a sequence, wait …) that AIs queue on '
        'the entity; the top one runs every update. Leave unchanged in a level.')),
    ('CEntityAnimated', 'Facing Backwards'): ('confirmed', '0x48f260, 0x48fc50, 0x48ebf0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the entity faces opposite to its movement angle (turned by π) and its animations play '
        'reversed, e.g. the player walking backwards while aiming. The player control sets it every frame.')),
    ('CEntityAnimated', 'Last Facing Backwards'): ('confirmed', '0x48f260', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: result of the last facing test: backwards when movement and aiming angles differ by more'
        ' than 95 degrees (85 once it was backwards, to avoid flicker).')),
    ('CEntityAnimated', 'Upper Body Present'): ('confirmed', '0x48eb50, 0x48f180', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: set at activation when a part answers "Is Upper Body Present"; then aiming and movement '
        'angles are separate (the upper body aims, the legs move). Activation only sets it, never clears it.')),
    ('CEntityAnimated', 'Synch Aiming And Moving'): ('confirmed', '0x48f300, 0x48fb50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state (default 1): with an upper body the aiming angle turns towards the movement angle each '
        "update at the model's turn speed (Player-category entities at once). The update switches it on again "
        'every time; the player control clears it while aiming freely.')),
    ('CEntityAnimated', 'Frame Index Locked'): ('confirmed', '0x48ff90, 0x48ffb0, 0x48feb0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the current frame is held; frame changes keep the locked frame until a behaviour unlocks'
        ' it.')),
    ('CEntityAnimated', 'Waiting For Discharge'): ('confirmed', '0x48ebb0, 0x48ebc0, 0x4c2130', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state of the weapon code: a shot is waiting to be fired. Changing the model with '
        'CSetModelAction and the "fix stuck gun" command clear it.')),
    ('CEntityAnimated', 'Still Shooting'): ('confirmed', '0x48ec30, 0x48ec40, 0x4c2130', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state of the weapon code: the entity is in the middle of shooting. Cleared like Waiting For '
        'Discharge (model change, "fix stuck gun").')),
    ('CEntityAnimated', 'Trying To Move'): ('confirmed', '0x491160, 0x4914d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: set every update of a movable entity while its target position differs from its '
        'position.')),
    ('CEntityAnimated', 'Tracking Updates Since Relocate'): ('confirmed', '0x48f300, 0x48fe40, 0x48fe30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: on after the entity was relocated; the updates are counted (up to 10) in "Debug/Num '
        'Updates Since Relocate". Touching triggers do not run their Enter Action for it during the first 4 '
        'updates.')),
    ('CEntityMovable', 'Friction'): ('confirmed', '0x490fc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Share of the velocity removed every update (0 = none, 1 = stops at once). It is applied per update, not '
        'per second, so its effect depends on the frame rate. Only while active and not stationary.')),
    ('CEntityMovable', 'Velocity X'): ('confirmed', '0x490fc0, 0x491160', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal speed in pixels per second; each update moves the target position by velocity × seconds (the '
        'move then goes through collision when Tries To Collide is set).')),
    ('CEntityMovable', 'Velocity Y'): ('confirmed', '0x490fc0, 0x491160', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Vertical speed in pixels per second (positive = down the screen); applied like Velocity X.')),
    ('CEntityMovable', 'Acceleration X'): ('confirmed', '0x490fc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal acceleration in pixels per second²; at the next update it is added to the velocity (× '
        'seconds) and then cleared, so a value in the level is a one-time push.')),
    ('CEntityMovable', 'Acceleration Y'): ('confirmed', '0x490fc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Vertical acceleration in pixels per second²; like Acceleration X it is applied once and then cleared.')),
    ('CEntityCharacter', 'Inventory'): ('confirmed', '0x49afd0, 0x49b040, 0x49b000', QT_TRANSLATE_NOOP(
        'fieldhelp', "The character's own inventory (items, weapons, ammunition); it is updated every frame and asked whether "
        'a weapon may fire. Resetting the fields gives the character a fresh empty inventory.')),
    ('CEntityCharacter', 'Home Pos X'): ('confirmed', '0x49a900, 0x49a8d0, 0x586050', QT_TRANSLATE_NOOP(
        'fieldhelp', "World x (pixels) of the character's home. CGuardPosAI walks back there when the character is too far "
        'away and patrols can turn back towards it; actions that place, relocate or spawn the character set it to'
        ' the new position.')),
    ('CEntityCharacter', 'Home Pos Y'): ('confirmed', '0x49a900, 0x49a8d0, 0x586050', QT_TRANSLATE_NOOP(
        'fieldhelp', "World y (pixels) of the character's home; see Home Pos X.")),
    ('CEntityCharacter', 'Weapons Use Amo'): ('confirmed', '0x472b50, 0x5b8010', QT_TRANSLATE_NOOP(
        'fieldhelp', "0/1: with 1 the character's weapons need their ammunition or energy (battery charge) to fire and use; "
        'with 0 they fire without using any.')),
    ('CEntityCharacter', 'LastDischargePosX'): ('confirmed', '0x49b1a0, 0x49b1d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state: x offset (pixels) of the last shot's muzzle relative to the character; turned by the "
        'aiming angle it serves as the discharge offset when aiming.')),
    ('CEntityCharacter', 'LastDischargePosY'): ('confirmed', '0x49b1a0, 0x49b1d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state: y offset (pixels) of the last shot's muzzle; see LastDischargePosX.")),
    ('CEntityCharacter', 'LastDischargeSequenceName'): ('confirmed', '0x49b1a0, 0x49b1d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: name of the sequence of the last shot; its rotation snaps the turned discharge offset.')),
    ('CEntityFlying', 'Max Acceleration'): ('confirmed', '0x430a40, 0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Flying speed: when a move behaviour drives the flier, its velocity along the movement angle is this '
        "value times the behaviour's play ratio, i.e. it acts as pixels per second despite the unit shown.")),
    ('CEntityWalking', 'Movement Speed'): ('confirmed', '0x430940, 0x498fa0, 0x46c1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the gait, Walk (0), Run (1) or Crouch (2). AIs set it as they go (patrols walk, chases '
        'run); move behaviours play the matching sequence, and an idle crouching walker uses IdleCrouch.')),
    ('CEntityOm', 'Angle Of Allowed Collisions'): ('confirmed', '0x526420, 0x526550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Radians, shown in degrees (default 0: the eye straight ahead in the facing direction).')),
    ('CEntityOm', 'Angle Plus Or Minus'): ('confirmed', '0x526420', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Default 0.1309 radians (7.5 degrees); radians, shown in degrees.')),
    ('CEntityOm', 'Has Been Hit In Eye'): ('confirmed', '0x526420, 0x526550', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state, set and cleared again within a single collision; leave unchanged in a level.')),
    ('CEntityOm', 'Collided While Rotating Action'): ('confirmed', '0x526570, 0x526600', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when turning Om would make it overlap an active, collideable object that is not a character; '
        'the turn is then taken back.')),
    ('CEntityOverlayWalking', 'Overlay Model'): ('confirmed', '0x49d0e0, 0x49d0a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "A second model drawn over the walking character's own model (e.g. a carried item or armour layer); it is"
        ' preloaded with the level and sent in multiplayer updates. No original level uses this class.')),
    ('CEntityProjectile', 'Shot Duration'): ('confirmed', '0x492150, 0x492080', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Lifetime in seconds (default 2), counted down while active. When it runs out the projectile takes its '
        'remaining hit points as "Unavoidable" damage and dies with its death type (e.g. explodes); without hit '
        'points it is simply removed.')),
    ('CEntityProjectile', 'Max Acceleration'): ('confirmed', '0x430a40, 0x430f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Flight speed: when a move behaviour drives the projectile, its velocity along the angle is this value, '
        'i.e. pixels per second despite the unit shown.')),
    ('CFreeRangePoly', 'Polygon'): ('verified', '0x4b6180, 0x4b61e0, 0x5480e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Outline in absolute world pixels (x1, y1, x2, y2, …; at most 25 points are read, a repeated point is '
        'skipped). A closed outline (last point = first) is hit inside, an open one within 4 pixels of its edges;'
        ' with Collideable it blocks movement like a wall.')),
    ('CRenderablePolygon', 'On Ground'): ('verified', '0x55dd90, 0x55dc30', QT_TRANSLATE_NOOP(
        'fieldhelp', '0/1 (default 1): 1 puts the surface into the ground queue (drawn before all objects, with shadows and '
        'ground marks: water, lava, floors); 0 into the object queue, sorted with the objects by its bottom edge '
        '+ YSort (e.g. black covers that hide what stands behind them).')),
    ('CRenderablePolygon', 'Render Type'): ('verified', '0x55d9f0, 0x55dd90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the surface is filled: Black, Shadow, Trans Blue, Trans Green, Trans Red (filled in that mode), '
        'Textured (Static Texture), Animated Texture or Warped (Warp Effect). Setting it restarts the animation '
        'time; Animated Texture and Warped are redrawn every frame, the others rest.')),
    ('CRenderablePolygon', 'YSort'): ('verified', '0x55dc30', QT_TRANSLATE_NOOP(
        'fieldhelp', "Pixels added to the polygon's bottom edge for the sort key (key = (bottom + YSort) × 8). It orders the "
        'surface against objects (On Ground 0) or against shadows and ground marks (On Ground 1); water uses -800'
        ' to stay below shadows.')),
    ('CRenderablePolygon', 'Cur Frame'): ('confirmed', '0x55dab0, 0x55d9f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Animation time of an Animated Texture in frames: each update adds the texture's frames per second × "
        'seconds and wraps at its frame count; the frame drawn is the integer part. A value in the level is a '
        'start offset; setting Render Type resets it to 0.')),
    ('CRenderablePolygon', 'Animated Texture'): ('confirmed', '0x55dd90, 0x55dab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animated texture (Cache/Animated Textures, e.g. Water Green Dark) used when Render Type is Animated '
        "Texture; default the list's first entry (!None).")),
    ('CRenderablePolygon', 'Static Texture'): ('confirmed', '0x55dd90', QT_TRANSLATE_NOOP(
        'fieldhelp', "Ground texture used when Render Type is Textured; default the list's first entry (01 Ivy).")),
    ('CRenderablePolygon', 'Warp Effect'): ('confirmed', '0x55dd90, 0x598420', QT_TRANSLATE_NOOP(
        'fieldhelp', "Water warp effect used when Render Type is Warped (the effect's current frame becomes the texture); "
        "default the list's first entry (!None).")),
    ('CWayPointsPolygon', 'Insertion Priority'): ('verified', '0x5383f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Order in which the outline is used when the way-point map is built: all Primary polygons first, then the'
        ' Secondary ones (default). Earlier points win, because a new way point needs the minimum distance to all'
        ' existing ones.')),
    ('CSimpleLayerPart', 'X'): ('confirmed', '0x571800, 0x4fe760', QT_TRANSLATE_NOOP(
        'fieldhelp', "World x coordinate in pixels of the part's position; setting it moves and re-lists the part.")),
    ('CSimpleLayerPart', 'Y'): ('confirmed', '0x571810, 0x4fe760', QT_TRANSLATE_NOOP(
        'fieldhelp', "World y coordinate in pixels of the part's position; setting it moves and re-lists the part.")),
    ('CLightningLayerPart', 'Z'): ('confirmed', '0x500080', QT_TRANSLATE_NOOP(
        'fieldhelp', "Height of the bolt's start above the position, in pixels (the start is drawn that much higher).")),
    ('CLightningLayerPart', 'X Length'): ('confirmed', '0x500080', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal distance in pixels from the start to the end of the bolt (default 100).')),
    ('CLightningLayerPart', 'Y Length'): ('confirmed', '0x500080, 0x4fe7d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Vertical distance in pixels from the start to the end of the bolt (default 25); it also sets how many '
        'draw items the bolt is split into (about one per 20 pixels).')),
    ('CLightningLayerPart', 'Height'): ('confirmed', '0x500080', QT_TRANSLATE_NOOP(
        'fieldhelp', "Pixels by which the bolt's end is raised (subtracted from Y Length).")),
    ('CLightningLayerPart', 'Width'): ('confirmed', '0x4fff60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How jagged the bolt is: each midpoint is moved sideways by a random amount up to ± this share of the '
        'segment length (0..1, default 0.25). The bolt is made anew on every draw.')),
    ('CLightningLayerPart', 'Min Segment Length'): ('confirmed', '0x4fff60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shortest segment in pixels (1..100, default 5): segments are split while a random length between this '
        'value and twice it still fits.')),
    ('CLightningLayerPart', 'Center Color'): ('confirmed', '0x4fe7d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Colour of the bolt's core line (default white).")),
    ('CLightningLayerPart', 'Edge Color'): ('confirmed', '0x4fe7d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Colour of the two glow lines drawn on both sides of the core (default 103, 35, 166).')),
    ('CUnderConstructionLayerPart', 'Text'): ('confirmed', '0x58fc60, 0x58fbb0, 0x58f100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text of the sign (default and when empty: "Under Construction"), drawn in the font Med Gold, wrapped to '
        'Max Width and centred horizontally on the position.')),
    ('CUnderConstructionLayerPart', 'Max Width'): ('confirmed', '0x58fc30, 0x58fbb0, 0x58fab0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width in pixels at which the text is wrapped (default 100); the sign's box is the wrapped text plus an "
        '8-pixel border.')),
    ('CUnderConstructionLayerPart', 'Border Texture'): ('confirmed', '0x58f100, 0x58f8a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Ground texture that fills the sign\'s 8-pixel border (default the texture "Under Construction"); the '
        'inside is filled with a fixed colour.')),
    ('CLayerSaveData', 'Custom Map Properties'): ('confirmed', '0x5b9e60, 0x4e6990', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The game\'s own level properties (CZaxLayerSaveData): "Compass Target", the object the HUD compass points'
        ' to. Empty in all original levels.')),
    ('CLayerSaveData', 'Music Mix'): ('confirmed', '0x4e7bf0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The level's music (CMusicMixerData): three music files below Music/ (full, medium, ambient) that the "
        'music mixer switches between.')),
    ('CLayerSaveData', 'Width'): ('verified', '0x4e69f0, 0x4e6a90, 0x4eae90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Map width in world pixels (default 4097). The object grid and the ground are sized from it when the '
        'level loads; the view and sound positions are limited by it.')),
    ('CLayerSaveData', 'Height'): ('verified', '0x4e69f0, 0x4e6a90, 0x4eae90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Map height in world pixels (default 4097); used like Width.')),
    ('CLayerSaveData', 'Action Queue'): ('confirmed', '0x41c700, 0x4e74a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: actions waiting to run (e.g. delayed ones); the queue is processed every update. Empty '
        'in all original levels; leave unchanged.')),
    ('CLayerSaveData', 'Suggested Num Players'): ('confirmed', '0x4d3c80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Recommended number of players (2-16, default 5); the multiplayer server dialog shows it as the lower '
        'number next to the map.')),
    ('CLayerSaveData', 'Max Players'): ('confirmed', '0x4d3c80, 0x4d3e20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Most players for this map (2-16; 0 = No Limit, treated as 16). The server dialog shows it next to the '
        'map and limits the player count to it.')),
    ('CLayerSaveData', 'Default Game Type'): ('confirmed', '0x4f4e70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Game type used when the level is started with "Default For Map" (default QuestMode).')),
    ('CLayerSaveData', 'Allowable Games'): ('confirmed', '0x4d3c80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Game types the map offers (default $All): the multiplayer server dialog lists the map only under the '
        'game types set here.')),
    ('CLayerSaveData', 'Has Begin Been Called'): ('confirmed', '0x4e74a0, 0x4e71b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state (0 in all original levels): at its first update the level activates its objects '
        '(their AIs begin) and resets the fog of war and the mini-map mapping, then sets this to 1. Leave at 0; '
        'with 1 that start-up is skipped.')),
    ('CLayerSaveData', 'Map Description'): ('confirmed', '0x4d3c80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Display name of the level (a Local.txt entry, so it can be translated); the multiplayer server dialog '
        'lists maps by it.')),
    ('CLayerSaveData', 'First Fire Action'): ('assumption', '0x4e5350, 0x4e6e80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'An owned action of the level. The reimplementation only loads, saves and deletes it; no code that runs '
        'it was found. Empty in the original levels checked.')),
    ('CLayerSaveData', 'First Load Action'): ('confirmed', '0x4f4890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run once when the level has finished loading (after preloading the assets), then deleted, so a '
        'save game does not run it again.')),
    ('CLayerSaveData', 'Environment Type'): ('confirmed', '0x4e6c20, 0x4186e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound environment setting (default Generic) without effect in the retail game: the setter stores or '
        'passes the value to code that does nothing with it (original bug 1.17). A non-default value changes '
        'nothing.')),
    ('CLayerSaveData', 'Rolloff'): ('confirmed', '0x4e6c50, 0x57c210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound fall-off factor (0-10, default 5) without effect in the retail game: the setter stores a value '
        'that only an unused debug drawing reads (original bug 1.17).')),
    ('CLayerSaveData', 'Environment Size'): ('confirmed', '0x4e6c80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound environment setting (default 7.5) without effect in the retail game: the setter stores or passes '
        'the value to code that does nothing with it (original bug 1.17). A non-default value changes nothing.')),
    ('CLayerSaveData', 'View Position'): ('confirmed', '0x4ed8f0, 0x4ed7f0, 0x4ea6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state: the camera position (top-left of the view in world pixels), kept inside the ground's "
        'size; the game moves it with the player. Leave unchanged in a level.')),
    ('CLayerSaveData', 'Int View Position'): ('confirmed', '0x4ed8f0, 0x4ea220', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: View Position rounded to whole pixels, the offset the view is drawn at. Leave unchanged '
        'in a level.')),
    ('CLayerSaveData', 'Partial File Name'): ('verified', '0x4eb670, 0x4ec090, 0x4eca80', QT_TRANSLATE_NOOP(
        'fieldhelp', "The level's path below Levels/ without extension; it names the .way file and the mini map image. On "
        'loading it is replaced by the name of the file actually loaded.')),
    ('CLayerSaveData', 'Team Info'): ('confirmed', '0x4f4950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'One CTeamInfo per team (index = team number): Spawn Point Name places a character of that team that '
        'comes without a start point name, Re-Spawn Point Name is used instead once its player was placed before.')),
    ('CLayerSaveData', 'Ambient Sounds'): ('confirmed', '0x4ea350, 0x4ee100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time list of ambient sounds of the level; while this level is the one that plays sounds they are '
        'placed relative to the listener every update. Empty in all original levels.')),
    ('CLayerSaveData', 'Shake Time'): ('confirmed', '0x4e9f00, 0x4ea350, 0x4e9f70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: seconds left of the current screen shake (started by CShakeScreenAction); counts down '
        'every update. 0 in all original levels.')),
    ('CLayerSaveData', 'Max Shake Time'): ('confirmed', '0x4e9f00, 0x4e9f70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: full length in seconds of the current screen shake; the shake fades out over its second '
        'half.')),
    ('CLayerSaveData', 'Pixels To Shake'): ('confirmed', '0x4e9f00, 0x4e9f70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the amplitude envelope (pixels) of the current screen shake, copied from the '
        'CShakeScreenAction.')),
    ('CLayerSaveData', 'Last Shake Delta'): ('confirmed', '0x4e9f70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the camera offset applied by the last shake step (taken away again before the next one).')),
    ('CLayerSaveData', 'Active Paths'): ('confirmed', '0x4e7180', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: cache of the paths characters are currently following (created on first use). Leave '
        'unchanged in a level.')),
    ('CLayerSaveData', 'Path Data'): ('verified', '0x4e70d0, 0x4eca80, 0x5383f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The way-point map (MinDistBetweenWayPoints, MaxDistToConnect). The game loads the network from the '
        "level's .way file or builds it with its own fixed values (20 and 39.8), whatever the level holds here.")),
    ('CLayerSaveData', 'Fog Of War'): ('confirmed', '0x4e71b0, 0x508000, 0x508180', QT_TRANSLATE_NOOP(
        'fieldhelp', "Fog map of the mini map (one pixel per mini-map pixel; 0 = uncovered); the view's area is uncovered as "
        'the player moves. When a level starts fresh (Has Begin Been Called 0) the game recreates it at mini-map '
        "size, fully covered, so the level's value only matters in save games.")),
    ('CLayerSaveData', 'Monitor'): ('confirmed', '0x4e74a0, 0x4e72a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time list of objects kept updated even when off-screen (optionally with an area around them), filled'
        ' by CPointOfIntrestAI. Empty in all original levels; leave unchanged.')),
    ('CLayerSaveData', 'Disable Mini-Map'): ('verified', '0x4e5350', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Has no effect: the game shows the mini map with 1 as well, no code reads the field (original bug 1.6).')),
    ('CLayerSaveData', 'Left Mini-Map Clipping'): ('confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', '0 = unclipped (default).')),
    ('CLayerSaveData', 'Top Mini-Map Clipping'): ('confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', '0 = unclipped (default).')),
    ('CLayerSaveData', 'Right Mini-Map Clipping'): ('confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', '0 = unclipped (default).')),
    ('CLayerSaveData', 'Bottom Mini-Map Clipping'): ('confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', '0 = unclipped (default).')),
    ('CLayerSaveData', 'MiniMap X Offset'): ('confirmed', '0x4ec3c0, 0x4e71b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the x offset of the world-to-mini-map mapping (mini-map x = world x × X Scale + X '
        'Offset, y likewise). Reset to 0 when the level starts and computed from the level size, the clippings '
        'and the mini-map size on first use; leave unchanged in a level.')),
    ('CLayerSaveData', 'MiniMap X Scale'): ('confirmed', '0x4ec3c0, 0x4e71b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the x scale of the world-to-mini-map mapping (mini-map x = world x × X Scale + X Offset,'
        ' y likewise). Reset to 0 when the level starts and computed from the level size, the clippings and the '
        'mini-map size on first use; leave unchanged in a level.')),
    ('CLayerSaveData', 'MiniMap Y Offset'): ('confirmed', '0x4ec3c0, 0x4e71b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the y offset of the world-to-mini-map mapping (mini-map x = world x × X Scale + X '
        'Offset, y likewise). Reset to 0 when the level starts and computed from the level size, the clippings '
        'and the mini-map size on first use; leave unchanged in a level.')),
    ('CLayerSaveData', 'MiniMap Y Scale'): ('confirmed', '0x4ec3c0, 0x4e71b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Run-time state: the y scale of the world-to-mini-map mapping (mini-map x = world x × X Scale + X Offset,'
        ' y likewise). Reset to 0 when the level starts and computed from the level size, the clippings and the '
        'mini-map size on first use; leave unchanged in a level.')),
    ('CLevelOfDifficulty', 'Human Readable Name'): ('confirmed', '0x5bf820, 0x4fdf70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shown as the button text of this difficulty in the "Select Difficulty" menu. A name left at the default '
        "text is replaced after loading by the difficulty file's name.")),
    ('CLevelOfDifficulty', 'Enemy Damage Percent'): ('confirmed', '0x48d380, 0x5bf690', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Applies to every damaged part in the "Enemy" category, before shields and AIs see the damage; stored as '
        'a fraction (1 = 100 %, range 0 to 3). The "Select Difficulty" menu also sorts the difficulties by this '
        'value, highest first.')),
    ('CLevelOfDifficulty', 'Player Damage Percent'): ('confirmed', '0x48d380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Applies to every damaged part in the "Player" category, before the shield absorbs anything; stored as a '
        'fraction (1 = 100 %, range 0 to 3).')),
    ('CLevelOfDifficulty', 'Weapon Drain Percent'): ('confirmed', '0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Multiplies the energy a player character's weapons take from the battery (per shot, and per second for "
        'continuous-fire weapons); fraction, 1 = 100 %, range 0 to 3.')),
    ('CLevelOfDifficulty', 'Weapon Get Pickup Percent'): ('confirmed', '0x475d40, 0x5b07d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Multiplies the charge of picked-up energy ammunition and batteries for a player's character; fraction, 1"
        ' = 100 %, range 0 to 3.')),
    ('CLevelOfDifficulty', 'Shield Drain Percent'): ('confirmed', '0x56da70', QT_TRANSLATE_NOOP(
        'fieldhelp', "Multiplies the damage a player's shield absorbs, i.e. how much shield charge a hit costs (on top of "
        '"Player Damage Percent"); the hit is fully absorbed either way. Fraction, 1 = 100 %, range 0 to 3.')),
    ('CLevelOfDifficulty', 'Shield Get Pickup Percent'): ('confirmed', '0x56f7c0, 0x56fd40', QT_TRANSLATE_NOOP(
        'fieldhelp', "Multiplies the charge a player's shield gets from shield pickups; fraction, 1 = 100 %, range 0 to 3.")),
    ('CListenerReference', 'Listener'): ('confirmed', '0x467d40, 0x467ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the object that receives this broadcaster\'s messages (e.g. "Died", "Delete"); '
        'written by the game when objects start listening. Leave unchanged in a level.')),
    ('CListenerReference', 'Member Offset'): ('confirmed', '0x467e60, 0x467d80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: every caller stores -1 here and no code reads it back (messages go to the '
        "listener's own handler). Leave unchanged.")),
    ('CListenerReference', 'Member Name'): ('confirmed', '0x467e60, 0x467d80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: every caller stores an empty text here and no code reads it back. Leave unchanged.')),
    ('CLoadSaveGameScreenOptions', 'Mission Detail Draw Style'): ('confirmed', '0x564b90', QT_TRANSLATE_NOOP(
        'fieldhelp', "Used for the mission objectives of the selected saved game in the load/save screen's details page.")),
    ('CMainMenuDisplayOptions', 'Left Fire Pos'): ('confirmed', '0x5be4a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the animated sequence "Fire Left" in the main menu, in pixels within the 640 × 480 menu area'
        ' (which sits at 80, 60 of the 800 × 600 screen).')),
    ('CMainMenuDisplayOptions', 'Right Fire Pos'): ('confirmed', '0x5be4a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the animated sequence "Fire Right" in the main menu, in pixels within the 640 × 480 menu '
        'area (which sits at 80, 60 of the 800 × 600 screen).')),
    ('CMainMenuDisplayOptions', 'Font'): ('confirmed', '0x4e3680, 0x4e2be0, 0x5be4a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Normal font of the menu buttons' text (main menu and the other menus drawn with the same text look); "
        'default "Med Gold".')),
    ('CMainMenuDisplayOptions', 'Hover Font'): ('confirmed', '0x4e3680, 0x4e2be0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of a menu button\'s text while the mouse is over it, drawn with the "Font Hover Effect" warp; '
        'default "Med Gold".')),
    ('CMainMenuDisplayOptions', 'Shadow Font'): ('confirmed', '0x4e3680, 0x4e2be0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the shadow drawn under every menu button text, 2 pixels down and right (1 pixel while pressed); '
        'default "Med Gold".')),
    ('CMainMenuDisplayOptions', 'Font Hover Effect'): ('confirmed', '0x4e3680, 0x4e2be0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sequence used as the warp texture that bends the hovered button text (with "Hover Font"); default "Menu '
        'Font Effect".')),
    ('CMainMenuDisplayOptions', 'Version Font'): ('confirmed', '0x5be4a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the version text ("Zax Version … Build …") in the main menu; default "Small Red".')),
    ('CMainMenuDisplayOptions', 'First Button Pos'): ('confirmed', '0x5be4a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Placement of the main menu buttons within the 640 × 480 menu area: x is the centre of the button column '
        '(all buttons as wide as the widest), y the top of the first button; the others follow below.')),
    ('CMaterialsGeneratorDisplayOptions', 'Window Y'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Top edge of the Materials Generator window in pixels on an 800 × 600 screen; on a 640-wide screen the '
        'window is moved 80 left and 120 up.')),
    ('CMaterialsGeneratorDisplayOptions', 'List X'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position of the item list (its column header; the grid follows below it) in the window, in pixels.')),
    ('CMaterialsGeneratorDisplayOptions', 'List Y'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', "Y position of the item list's column header in the window, in pixels; the grid starts below it.")),
    ('CMaterialsGeneratorDisplayOptions', 'List Width'): ('confirmed', '0x504050, 0x502960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width of the item list (header and grid) in pixels.')),
    ('CMaterialsGeneratorDisplayOptions', 'List Height'): ('confirmed', '0x502960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Total height of the item list in pixels; the grid gets this minus "List Header Height".')),
    ('CMaterialsGeneratorDisplayOptions', 'List Header Height'): ('confirmed', '0x504050, 0x502960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height of the column header row of the item list in pixels.')),
    ('CMaterialsGeneratorDisplayOptions', 'List Item Height'): ('confirmed', '0x502960, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height of one row of the item list in pixels; the 36-pixel item icon is centred vertically in it.')),
    ('CMaterialsGeneratorDisplayOptions', 'List Select Color'): ('assumption', '0x502960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Colour handed to the item grid window as its window colour; presumably the highlight of the selected row'
        ' (not checked visually).')),
    ('CMaterialsGeneratorDisplayOptions', 'Grid Line Color'): ('assumption', '0x502960, 0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Colour given to the item grid and its column header; presumably the colour of the grid and header lines '
        '(not checked visually).')),
    ('CMaterialsGeneratorDisplayOptions', 'Grid Scroll Bar Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', "Position of the item list's scroll bar in the window, in pixels.")),
    ('CMaterialsGeneratorDisplayOptions', 'Grid Scroll Bar Size'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width and height of the item list's scroll bar in pixels.")),
    ('CMaterialsGeneratorDisplayOptions', 'Text Margin'): ('confirmed', '0x502b10, 0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', "Horizontal inset in pixels of the cost texts: mineral names end this far before the mineral column's "
        'right edge (plus 12 for the icon) and the quantities start this far into their column; also handed to '
        'the column header.')),
    ('CMaterialsGeneratorDisplayOptions', 'Text Y Offset'): ('confirmed', '0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Vertical offset in pixels of the text in the "Usage" column (the ammunition item\'s name or the energy '
        'number) within a row.')),
    ('CMaterialsGeneratorDisplayOptions', 'Name Y Offset'): ('confirmed', '0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Vertical offset in pixels of the item name within a row.')),
    ('CMaterialsGeneratorDisplayOptions', 'Icon Width'): ('confirmed', '0x504050, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width in pixels of the first column, which shows the item's icon centred.")),
    ('CMaterialsGeneratorDisplayOptions', 'Name Width'): ('confirmed', '0x504050, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the item name column; names wrap at this width minus 4.')),
    ('CMaterialsGeneratorDisplayOptions', 'Usage Width'): ('confirmed', '0x504050, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the "Usage" column (the ammunition the item uses, or its energy number).')),
    ('CMaterialsGeneratorDisplayOptions', 'Cost A Width'): ('confirmed', '0x504050, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the first cost column, which lists the required minerals with icon and name.')),
    ('CMaterialsGeneratorDisplayOptions', 'Cost B Width'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the second cost column, which lists the quantity of each mineral.')),
    ('CMaterialsGeneratorDisplayOptions', 'Generate Sound'): ('confirmed', '0x503960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when a made item has an entry in the inventory (it becomes the current item); the HUD bar '
        'then slides and "Done Generating Sound" follows at its end.')),
    ('CMaterialsGeneratorDisplayOptions', 'Generate Non-Visable Item Sound'): ('confirmed', '0x503960', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played instead of "Generate Sound" when no inventory entry of the made item is found afterwards '
        '(e.g. it was merged into another item); the HUD bar\'s slide is skipped and no "Done Generating Sound" '
        'follows.')),
    ('CMaterialsGeneratorDisplayOptions', 'Done Generating Sound'): ('confirmed', '0x505a30', QT_TRANSLATE_NOOP(
        'fieldhelp', "Sound played when the HUD bar's slide after making an item with an inventory entry has finished.")),
    ('CMaterialsGeneratorDisplayOptions', 'Weapons Button Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position (top left, pixels in the window) of the "Weapons" tab (primary, secondary weapons and '
        'ammunition).')),
    ('CMaterialsGeneratorDisplayOptions', 'Shields Button Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position (top left, pixels in the window) of the "Shields" tab.')),
    ('CMaterialsGeneratorDisplayOptions', 'Power Button Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position (top left, pixels in the window) of the "Power" tab.')),
    ('CMaterialsGeneratorDisplayOptions', 'Misc Button Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position (top left, pixels in the window) of the "Misc" tab (all other categories).')),
    ('CMaterialsGeneratorDisplayOptions', 'Create Button Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position (top left, pixels in the window) of the button that makes the selected item.')),
    ('CMaterialsGeneratorDisplayOptions', 'Done Button Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position (top left, pixels in the window) of the "Done" button that closes the window.')),
    ('CMaterialsGeneratorDisplayOptions', 'Info Box Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Position of the description box (text of the selected item) in the window, in pixels.')),
    ('CMaterialsGeneratorDisplayOptions', 'Info Box Size'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width and height of the description box in pixels.')),
    ('CMaterialsGeneratorDisplayOptions', 'Info Box Scroll Bar Position'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', "Position of the description box's scroll bar in the window, in pixels.")),
    ('CMaterialsGeneratorDisplayOptions', 'Info Box Scroll Bar Size'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', "Width and height of the description box's scroll bar in pixels.")),
    ('CMaterialsGeneratorDisplayOptions', 'Info Box Margin'): ('confirmed', '0x503b80', QT_TRANSLATE_NOOP(
        'fieldhelp', "Inner margin of the description box's text in pixels.")),
    ('CMaterialsGeneratorDisplayOptions', 'Info Box Font'): ('confirmed', '0x503b80', QT_TRANSLATE_NOOP(
        'fieldhelp', "Font of the description box's text.")),
    ('CMaterialsGeneratorDisplayOptions', 'Primary Font'): ('confirmed', '0x504050, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Main font of the window: item names, mineral names and quantities in the list; also the (empty) header '
        'of the icon column.')),
    ('CMaterialsGeneratorDisplayOptions', 'Item Column Font'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', "Font of the item name column's header label only.")),
    ('CMaterialsGeneratorDisplayOptions', 'Amo Use Font'): ('confirmed', '0x504050, 0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the "Usage" column\'s header and of the ammunition item name shown in that column.')),
    ('CMaterialsGeneratorDisplayOptions', 'Energy Use Font'): ('confirmed', '0x502b10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the energy number shown in the "Usage" column for items without an ammunition item.')),
    ('CMaterialsGeneratorDisplayOptions', 'Mineral Column Font'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the mineral (first cost) column\'s header label only; the mineral names use "Primary Font".')),
    ('CMaterialsGeneratorDisplayOptions', 'Qty. Column Font'): ('confirmed', '0x504050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font of the quantity column\'s header label only; the quantities use "Primary Font".')),
    ('CMaterialsGeneratorDisplayOptions', 'After Generated Action'): ('confirmed', '0x503960', QT_TRANSLATE_NOOP(
        'fieldhelp', "It runs in the player character's layer with the character as instigator, after the minerals are used up"
        ' and the made-item sound was played.')),
    ('CMiniMapOverlay', 'MiniMap Overlay Frame Name'): ('confirmed', '0x507220', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of a frame image for a mini map overlay; nothing in the exe uses the class beyond its own '
        'registration, so the value has no effect.')),
    ('CMiniMapOverlay', 'Travel Distance'): ('confirmed', '0x507220', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A distance in pixels (default 70) for a mini map overlay; nothing in the exe uses the class beyond its '
        'own registration, so the value has no effect.')),
    ('CMiniMapOverlay', 'Height Offset'): ('confirmed', '0x507220', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A height offset in pixels (default 0) for a mini map overlay; nothing in the exe uses the class beyond '
        'its own registration, so the value has no effect.')),
    ('CMission', 'Mission Number'): ('confirmed', '0x512280, 0x5bcb60, 0x5bcc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of the mission, shown as "M<number>" in saved-game names and descriptions and used to sort saves.'
        ' -1 (default) takes it from the first digits of the "Description" text (e.g. "Log Entry 12 - …").')),
    ('CMission', 'ID Tag'): ('confirmed', '0x512800, 0x512d20, 0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Unique name of the mission: "CSelectMission" looks it up (case ignored), and "CDefineMission" refuses a '
        'mission whose tag is already defined. The in-game mission overlay shows it as the heading.')),
    ('CMission', 'Description'): ('confirmed', '0x510590, 0x509910, 0x512280', QT_TRANSLATE_NOOP(
        'fieldhelp', "Local.txt text of the mission (key and text): shown as the mission title on the inventory screen's "
        'mission page and above the objectives in the mission displays; its first digits give the mission number '
        'when "Mission Number" is -1.')),
    ('CMission', 'Objectives'): ('confirmed', '0x512170, 0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The mission\'s objectives ("CMissionObjective" and subclasses), in display order. "CAddMissionObjective" '
        'appends copies later; an objective whose "ID Tag" is already used is refused.')),
    ('CMission', 'Completed Action'): ('confirmed', '0x513b20, 0x513f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run once when an update or increment action leaves every objective of the mission complete; it is'
        ' deleted afterwards.')),
    ('CMission', 'Old Num Objectives'): ('confirmed', '0x512330, 0x5122f0, 0x512170', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the objective count before the last addition (the displays then show only that '
        'many); reset to -1 every game frame. Leave unchanged in a level.')),
    ('CMission', 'Par Stat Data List'): ('confirmed', '0x512350, 0x5525f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The mission\'s par ("typical") values for the quest statistics shown at the mission\'s end, one entry per '
        'statistic in the order of the quest game type; a statistic whose points depend on a par score needs its '
        'entry here.')),
    ('CMissionDisplayPageOptions', 'Page Title Area Width'): ('confirmed', '0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The title is centred horizontally in this width.')),
    ('CMissionDisplayPageOptions', 'Page Title Area Height'): ('confirmed', '0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The title is centred vertically in this height.')),
    ('CMissionDisplayPageOptions', 'Page Title Text'): ('confirmed', '0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Local.txt text, centred in the page title area.')),
    ('CMissionDisplayPageOptions', 'Mission Title Area X'): ('confirmed', '0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The mission title (the current mission\'s "Description") starts at this x plus "Mission Title Margin".')),
    ('CMissionDisplayPageOptions', 'Mission Title Area Height'): ('confirmed', '0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The mission title is centred vertically in this height.')),
    ('CMissionDisplayPageOptions', 'Mission Title Font'): ('confirmed', '0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The text shown is the current mission\'s "Description"; without a mission "No Mission Defined" appears in'
        ' the draw style\'s "Mission Normal Status Font" instead.')),
    ('CMissionDisplayPageOptions', 'Mission Detail Width'): ('confirmed', '0x50ffe0, 0x5101d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The objectives are drawn 5 pixels from the left and wrap at this width minus 10.')),
    ('CMissionDisplayPageOptions', 'Mission Detail Height'): ('confirmed', '0x50ffe0, 0x5101d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Also the least scroll height of the objectives list; longer lists scroll.')),
    ('CMissionDisplayPageOptions', 'Mission Detail Draw Style'): ('confirmed', '0x50ffe0, 0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Used for the objectives list of the inventory screen\'s mission page; its "Mission Normal Status Font" '
        'also shows "No Mission Defined".')),
    ('CMissionManager', 'Current Mission Index'): ('confirmed', '0x5127e0, 0x512d20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of the save game: index of the current mission in "Missions" (an index beyond the '
        'list means no current mission); set by "CDefineMission" and "CSelectMission".')),
    ('CMissionManager', 'Last Changed Time'): ('confirmed', '0x510e20, 0x509890', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: game time in seconds of the last mission or objective change. The in-game mission '
        'overlay computes the time since then but does not use the result.')),
    ('CMissionManager', 'Missions'): ('confirmed', '0x512d20, 0x512800', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of the save game: every mission defined so far by "CDefineMission" (copies), in '
        'order of definition.')),
    ('CMissionObjective', 'ID Tag'): ('confirmed', '0x512170, 0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the objective within its mission: the objective actions find it by this tag (case ignored), and '
        'a second objective with the same tag is refused. The in-game mission overlay draws it right-aligned just'
        ' left of the objective.')),
    ('CMissionObjective', 'Description'): ('confirmed', '0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Local.txt text of the objective, drawn in the draw style\'s "Mission Detail Font", followed by the '
        'status.')),
    ('CMissionObjective', 'Status'): ('confirmed', '0x510da0, 0x510df0, 0x510e20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Local.txt entry: the text is shown after the description; the key decides the state: containing '
        '"Complete" (but not "Incomplete") means complete, containing "Fail" means failed (case ignored). Usually'
        ' changed by "CUpdateMissionObjective".')),
    ('CMissionObjective', 'Completed Action'): ('confirmed', '0x510e20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Action run once when the objective's status becomes complete; deleted afterwards. Un-completing an "
        'objective only gives a warning.')),
    ('CMissionObjective', 'Old Objective'): ('confirmed', '0x510e20, 0x5122f0, 0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: a copy of the objective from before its last change, shown by the displays in its '
        'place until the next game frame deletes it. Leave empty in a level.')),
    ('CCountMissionObjective', 'Total Needed'): ('confirmed', '0x511010, 0x5113c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of increments ("CIncrementMissionObjective") needed; the objective counts as complete once '
        '"Current Count" reaches it. Default 2.')),
    ('CCountMissionObjective', 'Current Count'): ('confirmed', '0x5113c0, 0x5114d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Current count (the start value in a level, default 0); each increment adds 1 up to "Total Needed" and '
        'rewrites the status text from count and total.')),
    ('CSeriesMissionObjective', 'Next Status'): ('confirmed', '0x511940, 0x513f20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run (and kept) each time "CIncrementMissionObjective" targets this objective, typically one that '
        "sets the next status of a series; afterwards the mission's completion is checked as for an update.")),
    ('CMissionObjectiveDisplayOptions', 'Mission Detail Tab Stop'): ('confirmed', '0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In pixels: when the mission title is shown, the objectives are indented by this amount; wrapped text '
        'uses twice this value as its tab width. Default 10.')),
    ('CMissionObjectiveDisplayOptions', 'Mission Detail Spacing'): ('confirmed', '0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In pixels, added after the mission description and after every objective. Default 8.')),
    ('CMissionObjectiveDisplayOptions', 'Mission Normal Status Font'): ('confirmed', '0x509910, 0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', "Used for objectives that are neither complete nor failed; the inventory screen's mission page also shows"
        ' "No Mission Defined" in it.')),
    ('CMissionObjectiveDisplayOptions', 'Mission Done Status Font'): ('confirmed', '0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Completed objectives are additionally drawn at half opacity.')),
    ('CMissionOverWindowOptions', 'Mission Over Window Frame'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The window takes its size from this image.')),
    ('CMissionOverWindowOptions', 'Bottom Button Frame'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is drawn centred behind each bottom button; the wider of it and the pressed image sets the spacing of'
        ' the button row.')),
    ('CMissionOverWindowOptions', 'Bottom Button Pressed Frame'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', "It is the buttons' own image, drawn only while a button is pressed; it also sets the buttons' size.")),
    ('CMissionOverWindowOptions', 'Window Area Origin'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'With "Window Area Extent" it gives a rectangle that is tinted before the window art is drawn over it.')),
    ('CMissionOverWindowOptions', 'Window Area Extent'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width and height of the rectangle tinted behind the window art.')),
    ('CMissionOverWindowOptions', 'Title Center Point'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In the coordinates of the window art.')),
    ('CMissionOverWindowOptions', 'Bottom Buttons Center Point'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The bottom buttons are laid out in a row centred on this point (window art coordinates).')),
    ('CMissionOverWindowOptions', 'Drawing Origin'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'This area holds the message text and the statistics table on the left and the objectives list on the '
        'right.')),
    ('CMissionOverWindowOptions', 'Drawing Extent'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The objectives list gets its full height; the divider line runs from its top to its bottom.')),
    ('CMissionOverWindowOptions', 'Scroll Bar Origin'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The scroll bar scrolls the objectives list.')),
    ('CMissionOverWindowOptions', 'Draw Right-Left Divider'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The divider is a 2-pixel line in "Seperator Color" at the left edge of the objectives area.')),
    ('CMissionOverWindowOptions', 'Main Window Font'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', "It shows the window's message text, wrapped to the left column (not in the multiplayer window).")),
    ('CMissionOverWindowOptions', 'Mission Objectives Draw Style'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Used for the objectives list on the right side, with the mission's description as heading.")),
    ('CMissionOverWindowOptions', 'Seperator Color'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only drawn when "Draw Right-Left Divider" is on.')),
    ('CMissionOverWindowOptions', 'Drawing Left-Right Margins'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In pixels; applies to the message text, the statistics table and the objectives list.')),
    ('CMissionOverWindowOptions', 'Drawing Top-Bottom Margins'): ('confirmed', '0x50cab0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In pixels; also the gap between the message text and the statistics table.')),
    ('CMissionOverWindowOptions', 'Total Score Label Text'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Drawn beside the total at the bottom of the points column, only when the quest statistics award points.')),
    ('CMissionOverWindowOptions', 'Completed Title Font'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In the multiplayer variant of these options it is also the title font of the multiplayer end window.')),
    ('CMissionOverWindowOptions', 'Completed Title Text'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Local.txt text.')),
    ('CMissionOverWindowOptions', 'Continue Button Label'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shown in the mission completed window and in the multiplayer end window.')),
    ('CMissionOverWindowOptions', 'SaveGame Button Label'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shown only in the mission completed window.')),
    ('CMissionOverWindowOptions', 'Failed Title Text'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Local.txt text.')),
    ('CMissionOverWindowOptions', 'Load Game Button Label'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shown in the mission failed window.')),
    ('CMissionOverWindowOptions', 'Restart Mission Button Label'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shown in the mission failed window.')),
    ('CMissionOverWindowOptions', 'End Game Button Label'): ('confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shown in the mission failed window and in the multiplayer end window.')),
    ('CModel', 'Legacy Name'): ('assumption', '0x516b50', QT_TRANSLATE_NOOP(
        'fieldhelp', "Old name of the model kept from earlier file versions; the game only returns it through the model's name"
        ' getter and no gameplay code was found that uses it. Leave empty.')),
    ('CModel', 'Printable Name'): ('assumption', '0x5159b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Display name of the model. Only loaded and saved with the .mdl file; no game code was found that reads '
        'it.')),
    ('CModel', 'Description'): ('assumption', '0x5159b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Free description text of the model. Only loaded and saved with the .mdl file; no game code was found '
        'that reads it.')),
    ('CModel', 'Activity'): ('confirmed', '0x48ca40, 0x48cb90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'AIs ("Model Activity") shared by every destructable entity of this model: each frame they get the '
        "entity's update while it is active, and they are told about its collisions. Use it for behaviour that "
        'all instances of a model should have.')),
    ('CModel', 'Default Entity'): ('confirmed', '0x5176f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Template object for entities made from this model: when the game creates an entity of the model '
        '(spawning, projectiles, particles, explosions) it clones this object instead of a fresh object with '
        'default fields. Empty = a new object of the requested class.')),
    ('CModel', 'Hit Points'): ('confirmed', '0x48d150, 0x48d380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Health of entities with this model. Damage adds up until it reaches this value; then the entity is '
        'destroyed (death sound, explosion, "Destroyed Action"). 0 is shown as "Indestructible".')),
    ('CModel', 'Collide Damage'): ('confirmed', '0x48cb90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hit points of damage this model deals to a living destructable entity that collides with it, on every '
        'collision contact, of the type "Collide Damage Type". 0 = no collision damage.')),
    ('CModel', 'Collide Damage Type'): ('confirmed', '0x48cb90, 0x48f630', QT_TRANSLATE_NOOP(
        'fieldhelp', "Damage type (from the damage type list) used for this model's collide damage and also for its explosion "
        'radial damage.')),
    ('CModel', 'Closing Damage'): ('confirmed', '0x482170, 0x482710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'For doors: hit points per second dealt to living entities touching the door while it closes or is closed'
        ' (applied every 0.2 s as value × 0.2, type "Unavoidable"; victims are also turned randomly). 0 disables '
        'it. Default 10.')),
    ('CModel', 'Explosion Radial Damage'): ('confirmed', '0x48f630', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Damage dealt when an entity of this model dies: this many hit points within a radius of twice the value '
        '(in pixels) around its centre, of the "Collide Damage Type". 0 = no area damage.')),
    ('CModel', 'Sorting Y'): ('verified', '0x48abf0, 0x488d70', QT_TRANSLATE_NOOP(
        'fieldhelp', "Offset in pixels added to the entity's Y position when sorting the drawing order: larger values draw the"
        ' model in front of things at the same position. The model constructor presets it from its bounds '
        'polygon.')),
    ('CModel', 'Default Sequence'): ('confirmed', '0x5173b0, 0x5176f0, 0x48f4b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the sequence an entity of this model plays when it is created or gets the model '
        '(case-insensitive). If the model has no sequence of that name, the first sequence is used. Default '
        '"Idle".')),
    ('CModel', 'Activate Sound'): ('confirmed', '0x4825b0, 0x4c29f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when a door of this model opens, and when an activate action with "Play Activate Sound" '
        'activates an entity of this model.')),
    ('CModel', 'Close Sound'): ('confirmed', '0x482710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when a door of this model starts closing.')),
    ('CModel', 'Explosion'): ('confirmed', '0x48f590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model (from the model list) spawned as an explosion at the entity when it dies. Empty = none.')),
    ('CModel', 'Death Sound'): ('confirmed', '0x48f590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played when an entity of this model dies.')),
    ('CModel', 'Pain Sound'): ('confirmed', '0x48d380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played each time an entity of this model takes positive damage.')),
    ('CModel', 'Surface Type'): ('confirmed', '0x4e9e60, 0x4c0950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Surface type reported for points covered by an entity of this model (e.g. a bridge or platform); '
        'surface-dependent sounds such as footsteps then use it instead of the ground texture\'s surface. "!None" '
        '= use the ground below.')),
    ('CModel', 'Max Velocity'): ('confirmed', '0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Speed in pixels per second. Confirmed use: a projectile of this model is fired at this speed (plus the '
        "shooter's own velocity for the player's shots). Default 500.")),
    ('CModel', 'Turn Speed'): ('confirmed', '0x517510, 0x5787c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Maximum turning rate in degrees per second used when AI behaviours turn the entity toward a target or '
        'direction. Default 180.')),
    ('CModel', 'Bounce Factor'): ('confirmed', '0x491710, 0x4e91e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Elasticity of bounces off walls, 0 to 1: the share of the speed into the wall that is reflected (1 = '
        'full rebound, 0 = no rebound). The editor allows up to 5, but a value above 1 or below 0 stops the game '
        'with a fatal error when the entity moves.')),
    ('CModel', 'Min Bounce'): ('confirmed', '0x491710, 0x4e91e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Minimum rebound speed: a reflected speed component not above this value is dropped, so slow impacts no '
        'longer bounce. Values of 1.1 or more make the game log a warning. Default 0.1.')),
    ('CModel', 'Bounce Friction'): ('confirmed', '0x491710, 0x4e91e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Friction on each wall hit: the part of the movement along the wall is multiplied by (1 − value). 0 = no '
        'friction, 1 = sliding stops at once.')),
    ('CModel', 'Min Bounce Friction'): ('confirmed', '0x491710, 0x4e91e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'After a wall hit, a remaining sliding speed below this value is set to 0, so the object comes to rest. '
        'Default 0.1.')),
    ('CModel', 'Bounds Poly'): ('confirmed', '0x48a100', QT_TRANSLATE_NOOP(
        'fieldhelp', "Collision polygon of the model in pixels relative to the entity's position; used as the entity's shape "
        'for collisions and grid lookups (rectangle kind 3) and for the cached bounds.')),
    ('CModel', 'Also Render'): ('confirmed', '0x488d70, 0x48a100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Another model (from the model list) drawn together with this one at the entity, with its default '
        'sequence; its own "Also Render" is followed as well, and its frames count into the entity\'s bounds.')),
    ('CModel', 'Fidget Settings'): ('confirmed', '0x4990e0, 0x498f10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Fidget options of the model: while an entity of this model idles, it plays occasional fidget sequences '
        'according to these settings (an idle behaviour\'s "Override Fidget Options" takes precedence). Empty = no'
        ' fidgeting.')),
    ('CMultiPlayerGameData', 'Match Is Over'): ('confirmed', '0x51c650, 0x51c800', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of a multiplayer match: set when the match ends (time or score limit), cleared when'
        ' a new match starts; while set, players can signal ready. Leave unchanged.')),
    ('CMultiPlayerGameData', 'Players Ready To Start New Game'): ('confirmed', '0x51c800', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: number of players who are ready after the match ended; when half of the '
        'connections are ready a new match starts. Leave unchanged.')),
    ('CMusicMixer', 'Mixer Data'): ('confirmed', '0x51dbd0, 0x51e520', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The music mix currently in use: fade time and the three songs (full, medium, ambient). Normally filled '
        'by a "Set Music" action and at startup.')),
    ('CMusicMixer', 'Cur Song Index'): ('confirmed', '0x51e520, 0x51e470', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: track now playing (0 full mix, 1 medium mix, 2 ambient). Leave unchanged.')),
    ('CMusicMixer', 'Qued Song Index'): ('confirmed', '0x51e520, 0x51e470', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: track that will play once the current cross-fade is finished (0 full, 1 medium, 2 '
        'ambient). Leave unchanged.')),
    ('CNonInteractiveSequenceScene', 'New Camera Target'): ('confirmed', '0x521ef0, 0x5222a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'If the name finds no part (or is empty), the game reports an error and treats the scene as arrived at '
        "once. The player as target makes the player's camera tracker move there; any other part gets a temporary"
        ' camera tracker.')),
    ('CNonInteractiveSequenceScene', 'Camera Speed'): ('confirmed', '0x521ef0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Speed in pixels per second, default 150. 0 ("Immediately") makes the camera jump and the scene arrive at'
        ' once.')),
    ('CNonInteractiveSequenceScene', 'Camera Arrived Action'): ('confirmed', '0x522060, 0x522110', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The action runs with the player as instigator. The scene itself does not end on arrival; it ends only '
        'when an "End Current Non Interactive Sequence Scene" action is executed, after which the next scene '
        'starts.')),
    ('CObject', 'Dynamic Properties'): ('confirmed', '0x4831d0, 0x522380', QT_TRANSLATE_NOOP(
        'fieldhelp', 'List of extra properties stored on the object outside its regular fields (mainly values of older file '
        'versions that the class converts when loading). It is only written to the file when it has entries; '
        'normally empty.')),
    ('CObjectCollection', 'Num Objects'): ('assumption', '0x523c30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Array of object holders (each with one layer part). Only loaded and saved; no original game file uses '
        'this class and no game code reads it.')),
    ('CObjectHolder', 'Object'): ('assumption', '0x523a30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The layer part held by this holder (owned). Only loaded and saved; no game code was found that uses it.')),
    ('COtherMapList', 'ActionList'): ('confirmed', '0x41f130, 0x41f6c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: actions queued by "Other Map" actions, each with the name of the map it is meant '
        'for; they run (and are removed) when that map is entered. Leave unchanged.')),
    ('CParticleInfo', 'Model'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Model (from the model list) each particle of this kind is made from. It must have a projectile entity '
        'type; the particle lives for its age as a projectile.')),
    ('CParticleInfo', 'AI'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Particle AI (gravity, float, swirl …) cloned onto each emitted particle. Empty = the particle only flies'
        ' straight and does not animate.')),
    ('CParticleInfo', 'Animated'): ('confirmed', '0x52e2d0, 0x528a40', QT_TRANSLATE_NOOP(
        'fieldhelp', "1 = the particle's frame follows its age (passed to the particle's AI, so it has no effect without "
        '"AI"): without "Obey Sequence FPS" the whole sequence plays once over the particle\'s lifetime.')),
    ('CParticleInfo', 'Obey Sequence FPS'): ('confirmed', '0x528a40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'With "Animated": 1 = the particle plays its sequence at the sequence\'s own frames per second (looping) '
        'instead of stretching it over its lifetime.')),
    ('CParticleInfo', 'Tries To Collide'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 = particles of this kind test for collisions with the level while they move (they get the "Tries To '
        'Collide" flag).')),
    ('CParticleInfo', 'Collidable'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 = other objects can collide with particles of this kind ("Collideable" flag set); 0 clears it.')),
    ('CParticleInfo', 'Num Particles'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Particles of this kind emitted per burst (plus or minus "Num Particles Variance", never below 0). '
        'Default 1.')),
    ('CParticleInfo', 'Num Particles Variance'): ('confirmed', '0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Random variation of the count per burst: a random whole number between −value and +value is added to '
        '"Num Particles".')),
    ('CDiskParticleStartPositionType', 'Inside Radius'): ('confirmed', '0x52bed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Inner radius in pixels (an envelope that can change over time) of the ring on which particles start: '
        'each start point lies at a random distance between this radius and this radius plus "Outside Radius", in'
        ' the plane across the emission direction.')),
    ('CDiskParticleStartPositionType', 'Outside Radius'): ('confirmed', '0x52bed0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Thickness of the start ring in pixels (an envelope): added to "Inside Radius" to give the largest start '
        'distance; it is not an absolute outer radius.')),
    ('CDiskParticleStartPositionType', 'YX Ratio'): ('confirmed', '0x52bed0, 0x52e2d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Scale of the start offset's Y part, squashing the disk into an oval (1 = round). Also handed to the "
        "particles' AI as their Y-to-X ratio. Default 1.")),
    ('CDiskParticleStartPositionType', 'Use Cone Angle For Start Pos'): ('confirmed', '0x52bed0', QT_TRANSLATE_NOOP(
        'fieldhelp', '1 = each particle starts on the side of the disk its flight direction points to (the direction within '
        'the cone decides the angle on the disk); 0 = a random angle on the disk.')),
    ('CCylinderParticleStartPositionType', 'Height of Cylinder'): ('confirmed', '0x52cf70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Length in pixels (an envelope) of the cylinder along the emission direction: each particle starts at a '
        'random point between 0 and this value along that axis, on the disk given by the radii.')),
    ('CLineParticleStartPositionType', 'Center Length'): ('confirmed', '0x52c720', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Half length in pixels (an envelope) of a line through the emitter: each particle starts at a random '
        "point between −value and +value along the line (vertical before the system's face and trajectory turn "
        'it).')),
    ('CPathLineSegment', 'Flags'): ('confirmed', '0x53a0f0, 0x535860', QT_TRANSLATE_NOOP(
        'fieldhelp', "Run-time state of the way point map's segment, kept in the .way file: bit 0 set when built, bit 1 the "
        'path search found it walkable, bit 2 it has been checked. Leave unchanged.')),
    ('CPathLineSegment', 'MaxPassWidth'): ('confirmed', '0x539b40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Always set to 0 when a segment is built; no code reads it. Leave at 0.')),
    ('CPathLineSegment', 'Length'): ('confirmed', '0x53a0f0, 0x535860', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Length of the segment in pixels, computed when the way point map is built; the path search multiplies it'
        " by the mover's cost factor. Computed value, leave unchanged.")),
    ('CPathLineSegment', 'AngleAToB'): ('confirmed', '0x53a0f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Direction from way point A to way point B in radians (0 to 2π), computed when the map is built; no '
        'reader was found. Computed value, leave unchanged.')),
    ('CPathLineSegment', 'AIndex'): ('confirmed', '0x53a0f0, 0x53a0d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Index of the way point at one end of the segment in the map's way point list (−1 when unset). Computed "
        'when the map is built.')),
    ('CPathLineSegment', 'BIndex'): ('confirmed', '0x53a0f0, 0x53a0d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Index of the way point at the other end of the segment (−1 when unset). Computed when the map is built.')),
    ('CPathPointListListCache', 'Point List'): ('confirmed', '0x537370', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the pool of point lists that moving objects use for their current paths (free ones'
        ' are reused). Leave unchanged.')),
    ('CPathWayPoint', 'Flags'): ('assumption', '0x53a470', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Cleared when a way point is created; no code was found that reads it. Leave at 0.')),
    ('CPathWayPoint', 'Position X'): ('confirmed', '0x535860, 0x53a0f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'X position of the way point in level pixels; computed from the way point polygons when the map is built.')),
    ('CPathWayPoint', 'Position Y'): ('confirmed', '0x535860, 0x53a0f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Y position of the way point in level pixels; computed from the way point polygons when the map is built.')),
    ('CPlasmaTileMap', 'Blending'): ('confirmed', '0x541710', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Share (0 to 1) of each elevation band of the plasma ground that is cross-faded into the next texture of '
        'the texture list: 0.25 blends the top quarter of each band, 0 gives hard texture edges. In 8-bit colour '
        'only a few blend steps exist. Default 0.25.')),
    ('CPlayerWalkingControlSettings', 'Strafe Offset'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Probably meant for sideways (strafe) movement. The only code reading these settings (the player's "
        'walking control update) does not use this value; no other reader was found. Default 3.')),
    ('CPlayerWalkingControlSettings', 'Start Walk Mouse Dist'): ('confirmed', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Mouse control: share (0 to 1) of the cursor range beyond "Min Move Dist" where Zax starts walking; '
        'closer to the character he stands. Default 0.2.')),
    ('CPlayerWalkingControlSettings', 'Start Run Mouse Dist'): ('confirmed', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Mouse control: share (0 to 1) of the cursor range where Zax switches from walking to running. Default '
        '0.6.')),
    ('CPlayerWalkingControlSettings', 'Min Walk Ratio'): ('confirmed', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Walking speed ratio at "Start Walk Mouse Dist"; it rises linearly to 1 at "Start Run Mouse Dist". '
        'Default 0.2.')),
    ('CPlayerWalkingControlSettings', 'Min Run Ratio'): ('confirmed', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Running speed ratio at "Start Run Mouse Dist"; it rises linearly to 1 at the full cursor range. Default '
        '0.6.')),
    ('CPlayerWalkingControlSettings', 'Max Player Lives'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Probably a limit on the player's lives. The only code reading these settings (the player's walking "
        'control update) does not use this value; no other reader was found. Default 10.')),
    ('CPlayerWalkingControlSettings', 'Missile Trail Pufs Per Second'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Probably the rate of smoke puffs of missile trails. The only code reading these settings (the player's "
        'walking control update) does not use this value; no other reader was found. Default 120.')),
    ('CPlayerWalkingControlSettings', 'Missile Trail Frames Per Second'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Probably the animation rate of missile trail puffs. The only code reading these settings (the player's "
        'walking control update) does not use this value; no other reader was found. Default 30.')),
    ('CPlayerWalkingControlSettings', 'Min Move Dist'): ('confirmed', '0x542360, 0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Mouse control: dead zone in pixels around the character; the cursor must be farther away than this '
        'before the walking range starts. Default 80.')),
    ('CPlayerWalkingControlSettings', 'Max Cursor Distance'): ('confirmed', '0x542360, 0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Mouse control: size in pixels of the cursor range beyond "Min Move Dist"; at its end Zax moves at full '
        'speed. Default 100.')),
    ('CPlayerWalkingControlSettings', 'Player Max Turn Per Second'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Probably the player's maximum turn rate (stored in radians, shown in degrees). The only code reading "
        "these settings (the player's walking control update) does not use this value; no other reader was found."
        ' Default 45°.')),
    ('CPlayerWalkingControlSettings', 'Player Fine Turn Threshold'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Probably the angle below which the fine turn rate applies (radians, shown in degrees). The only code '
        "reading these settings (the player's walking control update) does not use this value; no other reader "
        'was found. Default 46°.')),
    ('CPlayerWalkingControlSettings', 'Player Max Fine Turn Per Second'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Probably the player's turn rate for small corrections (radians, shown in degrees). The only code reading"
        " these settings (the player's walking control update) does not use this value; no other reader was "
        'found. Default 22.5°.')),
    ('CPlayerWalkingControlSettings', 'Gun Height'): ('assumption', '0x543b60', QT_TRANSLATE_NOOP(
        'fieldhelp', "Probably the height in pixels of the player's gun above the ground. The only code reading these settings"
        " (the player's walking control update) does not use this value; no other reader was found. Default 39.")),
    ('CPointList', 'Is Available'): ('confirmed', '0x537370', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of the path cache: 1 = this point list is free for the next path, 0 = in use by a '
        'moving object. Leave unchanged.')),
    ('CPointList', 'Point'): ('confirmed', '0x535610, 0x536450', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the way point positions (pixels) of a path from start to goal, filled by the path '
        'search. Leave unchanged.')),
    ('CProjectileInfo', 'X offset'): ('confirmed', '0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Forward offset in pixels of this projectile's start point, added to the weapon's muzzle position along "
        "the shooter's facing.")),
    ('CProjectileInfo', 'Y offset'): ('confirmed', '0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Sideways offset in pixels of this projectile's start point, added to the muzzle position across the "
        "shooter's facing (squashed by the view's oval ratio).")),
    ('CProjectileInfo', 'Shot Angle'): ('confirmed', '0x4c4ee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Angle in degrees added to the aiming direction for this projectile, e.g. for spread shots (−360 to 360).')),
    ('CQuestGameTypeSpecificData', 'Stat Data List'): ('confirmed', '0x5528c0, 0x5527f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of the quest game: one data object per statistic (scores of this mission and of the'
        ' missions before). Leave unchanged.')),
    ('CQuestStat', 'Hide This Stat'): ('confirmed', '0x554b80, 0x5527f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A hidden statistic still counts toward the total score when it has a point value.')),
    ('CQuestStat', 'Hide Par Score'): ('confirmed', '0x554ce0, 0x5533e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "It suppresses the statistic's second row (the par label and the par values) in the mission-over window.")),
    ('CQuestStat', 'Point Value Weighting'): ('confirmed', '0x554d10, 0x555200', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Points = (cumulative value including this mission + par offset) × this weighting; non-zero also shows '
        'the points column.')),
    ('CQuestStat', 'Par Point Offset Weighting'): ('confirmed', '0x555200, 0x5582e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The par used is the cumulative par including this mission's. If it is non-zero and a mission has no par "
        'score for the statistic, the game reports an error and the statistic scores 0.')),
    ('CQuestStat', 'Stat Label'): ('confirmed', '0x5533e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is inserted into the first column\'s "Column Value Format" and into the game type\'s par label format.')),
    ('CQuestStat', 'Stat Label Font'): ('confirmed', '0x5533e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Also used for the par label of the second row. Default "Small Blue".')),
    ('CQuestStat', 'Stat Value Font'): ('confirmed', '0x5533e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Used for this mission\'s value, the total and the points. Default "Small Green".')),
    ('CQuestStatColumnInfo', 'Column Heading'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Columns in order: statistic name, this mission, total, points (the points heading only appears when some'
        ' statistic is scored).')),
    ('CQuestStatColumnInfo', 'Column Value Format'): ('confirmed', '0x5533e0', QT_TRANSLATE_NOOP(
        'fieldhelp', "In the first column '%s' is the statistic's label.")),
    ('CQuestStatColumnInfo', 'Heading Font'): ('confirmed', '0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Default "Small Gold".')),
    ('CQuestStatColumnInfo', 'X Offset'): ('confirmed', '0x5533e0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Horizontal position of the column in pixels from the left edge of the statistics area, for heading and '
        'values.')),
    ('CQuestStatColumnInfo', 'Width'): ('confirmed', '0x5533e0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width of the column in pixels; texts longer than this are word-wrapped. Default 30.')),
    ('CQuestStatColumnInfo', 'Justification'): ('confirmed', '0x5533e0, 0x50dc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Alignment of the heading and values within the column width (left, right, centre). Default "Justify '
        'Left".')),
    ('CQuestCounterData', 'Score This Mission'): ('confirmed', '0x554fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is added to "Cumulative Score" and reset to 0 when the mission ends. Saved quest state, normally left'
        ' unchanged.')),
    ('CQuestCounterData', 'Cumulative Score'): ('confirmed', '0x554fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Sum of all earlier missions; the total shown is this plus this mission's score. Saved quest state, "
        'normally left unchanged.')),
    ('CQuestCounterData', 'Cumulative Par Score'): ('confirmed', '0x554fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Each mission end adds that mission's par score. Saved quest state, normally left unchanged.")),
    ('CQuestFloatAccumulatorData', 'Score This Mission'): ('confirmed', '0x556c30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is added to "Cumulative Score" and reset to 0 when the mission ends. Saved quest state, normally left'
        ' unchanged.')),
    ('CQuestFloatAccumulatorData', 'Cumulative Score'): ('confirmed', '0x556c30', QT_TRANSLATE_NOOP(
        'fieldhelp', "Sum of all earlier missions; the total shown is this plus this mission's score. Saved quest state, "
        'normally left unchanged.')),
    ('CQuestFloatAccumulatorData', 'Cumulative Par Score'): ('confirmed', '0x556c30', QT_TRANSLATE_NOOP(
        'fieldhelp', "Each mission end adds that mission's par score. Saved quest state, normally left unchanged.")),
    ('CQuestPercentageData', 'Numerator This Mission'): ('confirmed', '0x55a100, 0x55a2b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Shown as numerator × 100 / denominator in percent; added to the cumulative value and reset at mission '
        'end. Saved quest state, normally left unchanged.')),
    ('CQuestPercentageData', 'Denominator This Mission'): ('confirmed', '0x55a100, 0x55a2b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A denominator not above 0 shows a placeholder instead of a percentage; added to the cumulative value and'
        ' reset at mission end. Saved quest state, normally left unchanged.')),
    ('CQuestPercentageData', 'Cumulative Numerator'): ('confirmed', '0x55a100, 0x55a350', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved quest state, normally left unchanged.')),
    ('CQuestPercentageData', 'Cumulative Denominator'): ('confirmed', '0x55a100, 0x55a350', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved quest state, normally left unchanged.')),
    ('CQuestPercentageData', 'Cumulative Par Numerator'): ('confirmed', '0x55a100', QT_TRANSLATE_NOOP(
        'fieldhelp', "Each mission end adds that mission's par numerator. Saved quest state, normally left unchanged.")),
    ('CQuestPercentageData', 'Cumulative Par Denominator'): ('confirmed', '0x55a100', QT_TRANSLATE_NOOP(
        'fieldhelp', "Each mission end adds that mission's par denominator. Saved quest state, normally left unchanged.")),
    ('CQuestTimeData', 'Time At Last Mission Mark'): ('confirmed', '0x5580c0, 0x558260', QT_TRANSLATE_NOOP(
        'fieldhelp', "The game clock reading at the end of the last mission; this mission's time is shown as clock minus this "
        'mark. Saved quest state, normally left unchanged.')),
    ('CQuestTimeData', 'Par Time Through Last Mission'): ('confirmed', '0x5580c0, 0x5582c0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Sum of the par times of all previous missions; each mission end adds that mission's par time. Saved "
        'quest state, normally left unchanged.')),
    ('CQuestCounterParScore', 'Par Score This Mission'): ('confirmed', '0x555180, 0x555200', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Set per mission in its par statistics list; shown in the par row and used when "Par Point Offset '
        'Weighting" is set.')),
    ('CQuestFloatAccumulatorParScore', 'Par Score This Mission'): ('confirmed', '0x556df0, 0x556e80', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Set per mission in its par statistics list; shown rounded down in the par row and used when "Par Point '
        'Offset Weighting" is set.')),
    ('CQuestPercentageParScore', 'Par Numerator This Mission'): ('confirmed', '0x55a300, 0x55a410', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The par percentage shown is numerator × 100 / denominator.')),
    ('CQuestPercentageParScore', 'Par Denominator This Mission'): ('confirmed', '0x55a300, 0x55a410', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A denominator not above 0 shows a placeholder instead of a par percentage.')),
    ('CQuestTimeParScore', 'Par Time This Mission'): ('confirmed', '0x558280, 0x5582e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A time (shown as a duration, assumed in seconds) set per mission in its par statistics list.')),
    ('CQuipCategory', 'Delay Before Saying'): ('confirmed', '0x55b770, 0x55b730, 0x55bd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds; 0 is treated as 0.01. A re-trigger while the quip is still waiting also restarts the "Minimum '
        'Time Between Saying" countdown.')),
    ('CQuipCategory', 'Minimum Time Between Saying'): ('confirmed', '0x55b770, 0x55b730, 0x55bd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds. The quip is also skipped if another voice is playing when its delay runs out.')),
    ('CQuipCategory', 'Condition'): ('confirmed', '0x55b050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The condition runs with the category as caller each time a "Say Quip" action fires; if it fails nothing '
        "happens (no timers are touched). After it, the action's probability still decides.")),
    ('CSimpleWarpEffect', 'Warp Effect'): ('confirmed', '0x571c50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animated texture (a sequence from the sequence list) through which the sprite is bent while the warp '
        "effect is on, e.g. when entities warp in or out; how strongly depends on the effect's strength, and the "
        "texture animates at the sequence's rate.")),
    ('CRules', 'First Map Name'): ('confirmed', '0x4f4e70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Map (level name) loaded when a new game starts without an explicit map. Default "Mission1 MainMap".')),
    ('CRules', 'First Map Spawn Point'): ('confirmed', '0x4f4e70', QT_TRANSLATE_NOOP(
        'fieldhelp', "Spawn point in the first map where the player starts a new game; empty = the map's default.")),
    ('CRules', 'Camera Bound Width'): ('confirmed', '0x4f5dd0, 0x4ed6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Width in pixels of the box around the screen centre in which the camera target can move before the view '
        'scrolls (camera modes 1 and 2). Default 142.')),
    ('CRules', 'Camera Bound Height'): ('confirmed', '0x4f5dd0, 0x4ed6e0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Height in pixels of the box around the screen centre in which the camera target can move before the view'
        ' scrolls. Default 106.')),
    ('CRules', 'Startup Song'): ('confirmed', '0x4f13a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Song (from the music folder) set as the ambient track of the music mixer and started when the game data '
        'is loaded.')),
    ('CRules', 'Window Font'): ('confirmed', '0x4f13a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Font (from the font list) given to the game's window system when the game data is loaded, used for its "
        'windows and dialogs.')),
    ('CRules', 'Custom Rules'): ('confirmed', '0x5a1f40', QT_TRANSLATE_NOOP(
        'fieldhelp', "The game's own rule object (CZaxCustomRules) with further option groups such as the player walking "
        'control settings and the Sphere of Zin options.')),
    ('CSequence', 'Frames Per Second'): ('confirmed', '0x4a5980, 0x55fee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Playback speed of the sequence in frames per second (default 30). Used by Auto-Animate layers and by the'
        ' behaviours and AIs that play the sequence.')),
    ('CSequence', 'Center Hot Spot'): ('confirmed', '0x56b440, 0x4b1db0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Load option (default on): moves each frame's hot spot (the point placed on the object's position) to the"
        " frame's centre; off keeps the source image's own origin. Only takes effect when the frames are built "
        'from the source images; the shipped .seq/.mdl files already contain the processed frames.')),
    ('CSequence', 'Blit Type'): ('verified', '0x56bf00, 0x4886a0, 0x56b440', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Blend mode the frames are drawn with: "Transparent Mask" (default, normal sprites with alpha edges), '
        '"Blend Black Bias" (smoke, fire) or "Blend Amplify Light" (light that brightens the background; black '
        'stays black). The two blend modes also change how frames are prepared when built from source images. A '
        'hue remap on the entity overrides it.')),
    ('CSequence', 'Blended With Black'): ('confirmed', '0x56b440', QT_TRANSLATE_NOOP(
        'fieldhelp', "Load option (default on): the source images' semi-transparent pixels are treated as pre-blended with "
        'black and are un-premultiplied (filter 7). Off skips that step; the blit types Blend Black Bias and '
        'Blend Amplify Light use their own filter instead. Only takes effect when the frames are built from the '
        'source images; the shipped .seq/.mdl files already contain the processed frames.')),
    ('CSequence', 'Crop Clor 0'): ('confirmed', '0x56b440', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Load option (default on; "Clor" is a typo for colour): crops each frame to its drawn (non-transparent) '
        'pixels, keeping the hot spot in place. Off keeps the full image size. Only takes effect when the frames '
        'are built from the source images; the shipped .seq/.mdl files already contain the processed frames.')),
    ('CSequence', 'Use 8 Bit Alpha'): ('confirmed', '0x56b440, 0x4b1db0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Load option (default off): keeps the full alpha channel by always using the 16-bit compressed frame '
        'format (also at 8-bit colour depth instead of five alpha bands) and lowers the cut-off below which '
        'pixels become fully transparent from alpha 5 to 3. Only takes effect when the frames are built from the '
        'source images; the shipped .seq/.mdl files already contain the processed frames.')),
    ('CSequence', 'Dither'): ('confirmed', '0x56b440, 0x4acda0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Load option (default off): dithers the frames when converting them to the display's colour depth instead"
        ' of plain rounding. Only takes effect when the frames are built from the source images; the shipped '
        '.seq/.mdl files already contain the processed frames.')),
    ('CSequence', 'X Offset'): ('confirmed', '0x56bca0, 0x56b570', QT_TRANSLATE_NOOP(
        'fieldhelp', "Horizontal draw offset in pixels (default 0): every frame's hot spot is moved so the image appears this "
        'many pixels further right (negative: left). Changing it moves all frames at once.')),
    ('CSequence', 'Y Offset'): ('confirmed', '0x56bda0, 0x56b570', QT_TRANSLATE_NOOP(
        'fieldhelp', "Vertical draw offset in pixels (default 0): every frame's hot spot is moved so the image appears this "
        'many pixels further down (negative: up). Changing it moves all frames at once.')),
    ('CFont', 'First ASCII'): ('confirmed', '0x4a6470, 0x4a6290', QT_TRANSLATE_NOOP(
        'fieldhelp', "Character code of the font's first glyph (default 32, the space); glyph n is character First ASCII + n. "
        'Characters outside the range draw the first glyph.')),
    ('CFont', 'Last ASCII'): ('confirmed', '0x4a6470, 0x4a5e90', QT_TRANSLATE_NOOP(
        'fieldhelp', "Character code of the font's last glyph (default 125). If it is below 95 (no lower-case letters), text "
        'drawn with the font is turned into capitals.')),
    ('CFont', 'Fixed Width'): ('confirmed', '0x4a5e90', QT_TRANSLATE_NOOP(
        'fieldhelp', "How the glyphs are cut from the font's source image (default on): on, the strip is divided into equal "
        "cells (image width / number of characters); off, each glyph ends at the next marker pixel in the image's"
        ' bottom row, giving proportional widths, and the base line is found from marker pixels as well.')),
    ('CRotationSequence', 'Num Rotations'): ('verified', '0x55f790, 0x55fdd0, 0x55fee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of facing directions the frames are split into (default 1; shipped models use 1, 3, 4, 6, 8, 12, '
        '20, 24 or 32). The frames are stored rotation by rotation; a value that does not divide the frame count '
        'evenly is refused and the old value kept.')),
    ('CRotationSequence', 'Editor Display Offset'): ('assumption', '0x55ed20', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only stored with the sequence (-100 in all shipped models); the game never uses it. Probably a display '
        'setting of the original editor.')),
    ('CRotationSequence', 'Render On Ground'): ('verified', '0x4886a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Draws this layer as part of the ground: it goes into the ground queue that is drawn before all other '
        "objects and is not lifted by the object's height (e.g. dirt, scorch marks, ground light).")),
    ('CRotationSequence', 'Is Shadow'): ('confirmed', '0x4886a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Marks the layer as a shadow: it is drawn at the object's position moved diagonally by the object's "
        "height (instead of raised by it), and the object's attachments are not drawn around it.")),
    ('CRotationSequence', 'Auto-Animate'): ('verified', '0x55fee0, 0x55e500, 0x4886a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Additional facts: the frame is taken from the game clock (frames per second of the sequence), so the '
        'layer animates even on objects that otherwise never change frame; without "Sync The Auto Animation" each'
        ' object gets its own phase.')),
    ('CRotationSequence', 'Sync The Auto Animation'): ('confirmed', '0x55fee0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Additional facts: the phase comes from the game clock alone, without the per-object offset.')),
    ('CRotationSequence', 'Editor Only'): ('verified', '0x517410, 0x517460', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Hides the layer in the game: such layers (handles, tool and marker graphics) are skipped when the '
        "model's layers are drawn, except when drawing is forced.")),
    ('CRotationSequence', 'Always Visible'): ('assumption', '0x517410', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Marks a layer that is drawn whatever sequence the object currently plays (e.g. pedestals of switches, '
        'floors of crates, ground light of light beams). In the game this comes from the layer chain stored in '
        'the model; no code was found that reads the flag itself.')),
    ('CRotationSequence', 'Rotational Offset'): ('verified', '0x55fdd0, 0x55fe90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Angle in radians (shown in degrees, -2π to 2π, default 0) at which rotation 0 starts; the facing angle '
        'minus this offset picks the rotation.')),
    ('CRotationSequence', 'Rotational Range'): ('verified', '0x55fdd0, 0x55fe90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Angle range in radians (shown in degrees, default 2π = full circle) that the rotations cover; each '
        'rotation spans Range / Num Rotations. Angles outside are brought into the range first.')),
    ('CRotationSequence', 'Sorting Y Offset'): ('verified', '0x55fc50, 0x4886a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Pixels added to the object's Y position when sorting this layer against other objects (default 0); "
        'larger values draw it later, i.e. in front. With cutting lines it applies to the strip left of the first'
        ' cut.')),
    ('CRotationSequence', 'Cutting Lines'): ('verified', '0x560270, 0x55fc50, 0x4886a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'List of vertical cuts (CVerticalCut) that split the layer into strips sorted separately, so e.g. a wall '
        'or tree can be partly in front of and partly behind a figure. Cuts should be in ascending X order.')),
    ('CRotationSequence', 'Trigger'): ('confirmed', '0x560300, 0x560480', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Per-frame triggers (CAnimationTrigger): entry n belongs to frame n of a rotation; its action runs when a'
        ' playing sequence passes that frame forwards or backwards (as set in the trigger). Used e.g. for '
        'footstep sounds and firing weapons on a frame.')),
    ('CSkeletonTransition', 'Trigger'): ('confirmed', '0x577a90, 0x576e50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How often the transition may fire: "Every Time" (default) each time the state change happens, "First '
        'Time" only once, "Once Per New Target" once and again after the AI gets a new target.')),
    ('CSkeletonTransition', 'From State'): ('confirmed', '0x577a90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'State the skeleton AI must be leaving for the transition to fire: Patrol, Pursue, Attack, Retreat, '
        'Investigate or "Any" (default).')),
    ('CSkeletonTransition', 'To State'): ('confirmed', '0x577a90, 0x5776d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'State the skeleton AI must be entering: one of the states, "Target Acquired", "Target Lost" or "Any" '
        '(default).')),
    ('CSkeletonTransition', 'Action'): ('confirmed', '0x577a90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action run when the transition fires, with the entity as caller and its current target (or the entity '
        'itself) as instigator.')),
    ('CSkeletonTransition', 'IsDone'): ('confirmed', '0x577a90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: set once a "First Time" or "Once Per New Target" transition has fired; leave '
        'unchanged in a level (set to 1 it never fires).')),
    ('CSpawnableItem', 'Weight'): ('confirmed', '0x4d0520', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Relative chance (1 to 999999, default 1) that a generator picks this entry: each spawn chooses one entry'
        ' at random with probability Weight / sum of all weights.')),
    ('CSpawnableCloneByName', 'Name'): ('confirmed', '0x4cf9a0, 0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Additional facts: the source is looked up in the generator's level when spawning and copied; the copy is"
        ' placed at the generator and, if the source was inactive, made active.')),
    ('CSpawnableEntity', 'CustomEntity'): ('confirmed', '0x4cf5d0, 0x4d05a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Entity template owned by this entry; each spawn places a copy of it at the generator.')),
    ('CSpawnableModel', 'Model'): ('confirmed', '0x4cf2c0, 0x5176f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Model to spawn: a copy of the model's default entity (or a plain entity) with its default sequence, "
        'placed at the generator.')),
    ('CSpecialAbilitylevelInfo', 'Description'): ('confirmed', '0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Text for this ability level, shown in the dialogue message when the character reaches the level ("... '
        'advanced to level N resulting in <description>"; default "increased power and longer durations").')),
    ('CSpecialAbilitylevelInfo', 'Charge Time'): ('confirmed', '0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds the special ability item needs to charge from empty to full at this level (default 10).')),
    ('CSpecialAbilitylevelInfo', 'Duration'): ('confirmed', '0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Seconds a full charge lasts while the ability is discharging at this level (default 1); when it is empty'
        ' the ability stops and the Deactivate Action runs.')),
    ('CSpecialAbilitylevelInfo', 'Activate Sound'): ('assumption', '0x5804d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound meant for activating the ability. Only saved and loaded: no code in the game reads it (nothing in '
        'the release activates special abilities).')),
    ('CSpecialAbilitylevelInfo', 'Activate Action'): ('assumption', '0x5804d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Action meant to run when the ability is activated. Only saved and loaded: no code in the game reads it '
        '(nothing in the release activates special abilities).')),
    ('CSpecialAbilitylevelInfo', 'Deactivate Action'): ('confirmed', '0x580070', QT_TRANSLATE_NOOP(
        'fieldhelp', "Action run (with the player's character) when a discharging ability at this level runs empty.")),
    ('CSphereOfZinData', 'Trigger List'): ('confirmed', '0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', "Thresholds (CThresholdTrigger) on the Sphere of Zin's charge: each fires its action when the charge "
        'crosses its value in the chosen direction.')),
    ('CSphereOfZinOptions', 'Evil Unit Lenght'): ('confirmed', '0x584d40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Squared distance in pixels² (default 40000, i.e. 200 pixels; Rules.txt sets 102400, i.e. 320 pixels).')),
    ('CSphereOfZinOptions', 'Apply Ceiling Prematurely'): ('confirmed', '0x584d40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Default 1.')),
    ('CStatsInventoryItem', 'Item Catagory'): ('confirmed', '0x5b7e20, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Where the line appears on the save game\'s statistics: "General Item" on the left page, "Weapon Or Ammo" '
        'on the right page; "NOT AN ITEM" (the default of a new object) hides it.')),
    ('CStatsInventoryItem', 'Label Text'): ('confirmed', '0x5b7e20, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', "Name column of the statistics line (for items the game fills in the item's display name).")),
    ('CStatsInventoryItem', 'Label Color'): ('confirmed', '0x5aedf0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font colour of the label: Red, Yellow (gold), Green or Blue (the small fonts of those colours).')),
    ('CStatsInventoryItem', 'Quantity Text'): ('confirmed', '0x5b7e20, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Value column of the statistics line (for items the game writes "Qty <count>").')),
    ('CStatsInventoryItem', 'Quantity Color'): ('confirmed', '0x5aedf0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Font colour of the value: Red, Yellow (gold), Green or Blue.')),
    ('CSwappedLayerFilenameMapping', 'Partial Layer Name'): ('confirmed', '0x5892b0, 0x5893c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of the level cache: the level file name (with .zax) this entry stands for; leave '
        'unchanged.')),
    ('CSwappedLayerFilenameMapping', 'Current Temp File'): ('confirmed', '0x5892b0, 0x5893c0, 0x589db0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: temporary file holding the level's current state since the mission started; it is "
        'loaded instead of the original level file. Leave unchanged.')),
    ('CSwappedLayerFilenameMapping', 'Mission Temp File'): ('confirmed', '0x5892b0, 0x589cc0, 0x589db0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state: temporary file with the level's state at the start of the current mission, used "
        'when the mission is restarted. Leave unchanged.')),
    ('CSwappedLayerFilenameMapping', 'Has Expired'): ('confirmed', '0x589570, 0x5899b0, 0x5892b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the level was expired by the script (loading it then gives the "Expired Error" '
        'level). Leave unchanged.')),
    ('CSwappedLayerFilenameMapping', 'Expired This Mission'): ('confirmed', '0x589cc0, 0x589db0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the expiry happened during the current mission, so a mission restart undoes it. '
        'Leave unchanged.')),
    ('CSwappedLayerFilenameMappingTable', 'Layer Mapping Array'): ('confirmed', '0x5893c0, 0x589570', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: one entry per level changed or expired during play (the level cache). Leave '
        'unchanged.')),
    ('CSwappedLayerFilenameMappingTable', 'Mission Marker Temp File'): ('confirmed', '0x589db0, 0x589cc0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: temporary save made at the start of the current mission, used to restart it. Leave'
        ' unchanged.')),
    ('CSwappedLayerFilenameMappingTable', 'LRU LayerSaveData Array'): ('confirmed', '0x589db0, 0x589a50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the loaded levels in order of last use; when more than three are cached, the '
        'oldest one (unless it is the current one) is saved to its temp file and unloaded. Leave unchanged.')),
    ('CTeamInfo', 'Spawn Point Name'): ('confirmed', '0x4f4950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of the spawn point object where a figure of this team is placed when it enters the level without a '
        "named start point. The entry's index in the team list is the team number (teams beyond the list use the "
        'last entry).')),
    ('CTeamInfo', 'Re-Spawn Point Name'): ('confirmed', '0x4f4950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Spawn point used instead of "Spawn Point Name" when the figure\'s player has already been placed before '
        '(a re-spawn); empty means the normal spawn point. Multiplayer levels use "random".')),
    ('CTeamInfo', 'Model Type'): ('assumption', '0x4e4640', QT_TRANSLATE_NOOP(
        'fieldhelp', "Model meant for this team's figures. No code reading it was found; all shipped levels leave it at "
        '"!Unknown Model".')),
    ('CThresholdTrigger', 'Threshold Value'): ('confirmed', '0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', "Additional facts: the value compared is the Sphere of Zin's charge, checked once per update between the "
        'previous and the current charge.')),
    ('CThresholdTrigger', 'Re-Trigger Amount'): ('confirmed', '0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Default 5.')),
    ('CThresholdTrigger', 'Threshold Action'): ('confirmed', '0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Additional facts: it runs in the level of the entity holding the sphere, with that entity as instigator.')),
    ('CThresholdTrigger', 'Trigger Direction'): ('confirmed', '0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Values: "Increasing" (default), "Decreasing", "Either Direction".')),
    ('CUpdateMonitorInfo', 'Update Part'): ('confirmed', '0x4e72a0, 0x4e7330', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the object the level keeps updating even off screen (the player, camera targets, '
        'objects of scripted sequences). Entries are added and removed by the game.')),
    ('CUpdateMonitorInfo', 'Half Width'): ('confirmed', '0x4e72a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Half width in pixels of the area around the monitored object in which all objects are updated as well; 0'
        ' updates only the object itself (both half sizes must be non-zero). Not initialised by the original '
        'constructor.')),
    ('CUpdateMonitorInfo', 'Half Height'): ('confirmed', '0x4e72a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Half height in pixels of the area around the monitored object in which all objects are updated as well; '
        '0 updates only the object itself. Not initialised by the original constructor.')),
    ('CUpdateMonitorList', 'Monitor List'): ('confirmed', '0x4e72a0, 0x4e5090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: the objects the level updates every frame regardless of the view (with an optional'
        ' area around each). The game adds and removes entries itself; an entry is dropped when its object is '
        'deleted or leaves the level.')),
    ('CUserDefinedClassRef', 'Class Definition'): ('confirmed', '0x590400, 0x5906a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of a user-defined class (a .UDC file); the game uses a copy of the object stored there. No .UDC '
        'files exist in the game data.')),
    ('CVerticalCut', 'Cut Offset'): ('verified', '0x560270', QT_TRANSLATE_NOOP(
        'fieldhelp', "X position of the cut in pixels, relative to the object's position (negative: left).")),
    ('CVerticalCut', 'Strip Sorting Y Offset'): ('verified', '0x55fc50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sorting offset in pixels of the strip to the right of this cut; it replaces the sequence\'s "Sorting Y '
        'Offset" for that strip (not added to it).')),
    ('CVoiceLogDisplayPageOptions', 'Page Title Area X'): ('confirmed', '0x595210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the page; the title is centred horizontally and vertically in this area.')),
    ('CVoiceLogDisplayPageOptions', 'Page Title Area Y'): ('confirmed', '0x595210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the page; the title is centred in the area.')),
    ('CVoiceLogDisplayPageOptions', 'Page Title Area Width'): ('confirmed', '0x595210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels; used only to centre the title, the text is not clipped.')),
    ('CVoiceLogDisplayPageOptions', 'Page Title Area Height'): ('confirmed', '0x595210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels; used only to centre the title vertically.')),
    ('CVoiceLogDisplayPageOptions', 'Page Title Text'): ('confirmed', '0x595210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A localisable text entry (default "Voice Log").')),
    ('CVoiceLogDisplayPageOptions', 'Page Title Font'): ('confirmed', '0x595210', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of a font from the font list.')),
    ('CVoiceLogDisplayPageOptions', 'Column Header X Position'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'Column Header Y Position'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'Column Header Width'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels; when "Dialog Column Width" is 0 the last column fills the rest of this width.')),
    ('CVoiceLogDisplayPageOptions', 'Column Header Height'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels.')),
    ('CVoiceLogDisplayPageOptions', 'Time Column Label'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A localisable text entry (default "How long ago"); the column shows the time since the line was said.')),
    ('CVoiceLogDisplayPageOptions', 'Time Column Width'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels (default 100); set once when the page is first laid out.')),
    ('CVoiceLogDisplayPageOptions', 'Speaker Column Label'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A localisable text entry (default "Who said").')),
    ('CVoiceLogDisplayPageOptions', 'Speaker Column Width'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels (default 80); set once when the page is first laid out.')),
    ('CVoiceLogDisplayPageOptions', 'Dialog Column Label'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A localisable text entry (default "What was said"); lines longer than 80 characters are shortened with '
        '"...".')),
    ('CVoiceLogDisplayPageOptions', 'Dialog Column Width'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels (default 80); 0 makes the column fill the rest of the header width.')),
    ('CVoiceLogDisplayPageOptions', 'Column Header Font'): ('confirmed', '0x5948b0, 0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Has no effect in the game.')),
    ('CVoiceLogDisplayPageOptions', 'List X Position'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'List Y Position'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'List Width'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels.')),
    ('CVoiceLogDisplayPageOptions', 'List Height'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels.')),
    ('CVoiceLogDisplayPageOptions', 'List Font'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name of a font from the font list.')),
    ('CVoiceLogDisplayPageOptions', 'Scroll Bar X Pos'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'Scroll Bar Y Pos'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'Scroll Bar Width'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels.')),
    ('CVoiceLogDisplayPageOptions', 'Scroll Bar Height'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button X Pos'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Y Pos'): ('confirmed', '0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Pixels, relative to the voice log page of the inventory screen.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Width'): ('confirmed', '0x5948b0, 0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Has no effect in the game.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Height'): ('confirmed', '0x5948b0, 0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Has no effect in the game.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Text'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'A localisable text entry (default "Replay"). The button replays the selected line and the lines recorded'
        ' at the same moment after it.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Font'): ('confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Has no effect in the game.')),
    ('CVoiceLogElement', 'Dialog Action'): ('confirmed', '0x592900, 0x5953d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state of the voice log: a copy of the dialogue action that said the line; Replay runs it '
        'again. Leave unchanged.')),
    ('CVoiceLogElement', 'When Said'): ('confirmed', '0x592900, 0x592770', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: game time in seconds when the line was said; the list shows the time since then '
        'and sorts by it. Leave unchanged.')),
    ('CVoiceLogElement', 'Order Said'): ('confirmed', '0x592900, 0x5959d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved run-time state: running number among lines said at the same moment (0 for the first), used to keep'
        ' their order. Leave unchanged.')),
    ('CWaterWarpEffect', 'V1 Wave'): ('confirmed', '0x597690, 0x597780, 0x597880', QT_TRANSLATE_NOOP(
        'fieldhelp', 'First of the two wave forms that shift each column of the 128 × 128 water texture up and down; the two V'
        ' waves are added.')),
    ('CWaterWarpEffect', 'V2 Wave'): ('confirmed', '0x597690, 0x597780, 0x597880', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Second wave form for the vertical shift of each column of the water texture; added to V1.')),
    ('CWaterWarpEffect', 'H1 Wave'): ('confirmed', '0x597690, 0x597780, 0x597880', QT_TRANSLATE_NOOP(
        'fieldhelp', 'First of the two wave forms that shift each row of the 128 × 128 water texture left and right; the two H'
        ' waves are added.')),
    ('CWaterWarpEffect', 'H2 Wave'): ('confirmed', '0x597690, 0x597780, 0x597880', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Second wave form for the horizontal shift of each row of the water texture; added to H1.')),
    ('CWaterWarpEffect', 'Show Grid'): ('assumption', '0x5970a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only saved and loaded; the game never reads it. Probably a preview aid of the original editor.')),
    ('CWaterWarpEffectFrame', 'Render Type'): ('confirmed', '0x598420', QT_TRANSLATE_NOOP(
        'fieldhelp', 'How the texture is bent: "Horizontal" (rows only), "Vertical" (columns only), "Horizontal Then Vertical"'
        ' (default, both), "Vertical Then Horizontal" (both, 16-bit colour only) or "Horizontal Then Vertical '
        'Animated" (both, using the animated texture).')),
    ('CWaterWarpEffectFrame', 'Static Texture'): ('confirmed', '0x598420', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Ground texture that is bent by the waves for all render types except the animated one.')),
    ('CWaterWarpEffectFrame', 'Animated Texture'): ('confirmed', '0x598420', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Animated texture used by "Horizontal Then Vertical Animated": its frame follows the game time at the '
        "texture's own frames per second, then it is bent by the waves.")),
    ('CWaterWaveFormData', 'Num Waves'): ('confirmed', '0x596de0, 0x597690', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Number of full wave cycles across the 128-pixel texture (0 to 16, default 4); the wave table is rebuilt '
        'when it changes.')),
    ('CWaterWaveFormData', 'Amplitude'): ('confirmed', '0x596d20, 0x597690', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Largest shift of a row or column in pixels (0 to 30, default 2).')),
    ('CWaterWaveFormData', 'Pixels Per Second'): ('confirmed', '0x596d80, 0x597690', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Speed at which the wave pattern moves along the texture, in pixels per second (-100 to 100, default 15; '
        'negative reverses the direction).')),
    ('CWayPointMap', 'MinDistBetweenWayPoints'): ('verified', '0x5383f0, 0x5380d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Minimum spacing in pixels between generated way points. The game keeps the value stored in the level's "
        ".way file and, when it builds a missing .way, uses its own fixed value 20, so the level's setting has no"
        ' effect.')),
    ('CWayPointMap', 'MaxDistToConnect'): ('verified', '0x538ae0, 0x5386b0, 0x5383f0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Largest distance in pixels at which two way points are joined; path searches also use it to find the way'
        " points near start and end. The game keeps the .way file's value and builds missing maps with 39 (39.8 "
        "truncated), so the level's setting has no effect.")),
    ('CWayPointPath', 'Start Point'): ('confirmed', '0x536d20, 0x5386b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Start of the move in pixels.')),
    ('CWayPointPath', 'End Point'): ('confirmed', '0x536d20, 0x5386b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Destination in pixels.')),
    ('CWayPointPath', 'Length'): ('confirmed', '0x536d20, 0x5386b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Straight distance from start to end in pixels; above 1600 no path is searched.')),
    ('CWayPointPath', 'Max Dist To Travel'): ('confirmed', '0x536d20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Set to twice the length; nothing reads it.')),
    ('CWayPointPath', 'Num Failed Paths'): ('confirmed', '0x536d20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Reset to 0 at each move; nothing reads it.')),
    ('CWayPointPath', 'Max Failed Paths'): ('confirmed', '0x536d20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Set to 1 at each move; nothing reads it.')),
    ('CWayPointPath', 'Pos To Move Index'): ('confirmed', '0x536e70, 0x536f40', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Index of the path point the object is heading for.')),
    ('CWayPointPath', 'Dist So Far'): ('confirmed', '0x536d20', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        'unchanged in a level. Reset to 0 at each move; nothing reads it.')),
    ('CWayPointPath', 'Path'): ('confirmed', '0x5386b0, 0x536e70', QT_TRANSLATE_NOOP(
        'fieldhelp', "Saved run-time state of a moving object's current path; rewritten whenever a new move starts. Leave "
        "unchanged in a level. Reference to the found list of path points in the level's path cache.")),
    ('CZaxSaveData', 'Mission Manager'): ('confirmed', '0x5127e0, 0x5bc2a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved game state (save games only, not used in levels). The mission manager with the missions and their '
        'progress.')),
    ('CZaxSaveData', 'Voice Log Array Data'): ('confirmed', '0x5bb9a0, 0x592900', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved game state (save games only, not used in levels). The lines of the voice log (CVoiceLogElement).')),
    ('CZaxSaveData', 'NonInteractive Sequence'): ('confirmed', '0x5a2b10, 0x5a2b60, 0x5a2b90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved game state (save games only, not used in levels). The scripted (non-interactive) sequence playing '
        'when the game was saved.')),
    ('CZaxSaveData', 'GameType Specific Data'): ('confirmed', '0x5bb160', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved game state (save games only, not used in levels). Data of the game type, e.g. the quest progress.')),
    ('CZaxSaveData', 'Difficulty'): ('confirmed', '0x5bb780, 0x5a0090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Saved game state (save games only, not used in levels). The chosen difficulty level (default "Normal").')),
    ('CZaxSaveGameStats', 'Save Date and Time'): ('confirmed', '0x5bc2a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Date and time of the '
        'save as text.')),
    ('CZaxSaveGameStats', 'SaveDateAndTimeNumeric'): ('confirmed', '0x5bc2a0, 0x5bcc10', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Time of the save as a '
        'number, used to sort saves (newest first).')),
    ('CZaxSaveGameStats', 'Current Mission'): ('confirmed', '0x5bc2a0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Copy of the mission '
        'active when saving (shown on the mission details page).')),
    ('CZaxSaveGameStats', 'Screen Shot'): ('confirmed', '0x5bc2a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. 200 × 150 picture of '
        'the game view at the moment of saving.')),
    ('CZaxSaveGameStats', 'Player Health'): ('confirmed', '0x5bc2a0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', "Save game summary shown on the load/save screen; filled by the game when saving. Hit points the player's"
        ' character had left.')),
    ('CZaxSaveGameStats', 'Elapsed Time'): ('confirmed', '0x5bc2a0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Playing time.')),
    ('CZaxSaveGameStats', 'Map Name'): ('confirmed', '0x5bc2a0, 0x5bc810', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Name of the current '
        'level.')),
    ('CZaxSaveGameStats', 'Ore In Inventory'): ('confirmed', '0x5bc2a0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Number of ore deposits '
        'the player carried.')),
    ('CZaxSaveGameStats', 'Crystals In Inventory'): ('confirmed', '0x5bc2a0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Number of crystals the '
        'player carried.')),
    ('CZaxSaveGameStats', 'SaveGame FileName'): ('confirmed', '0x5bc2a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. File the save was '
        'written to (SaveGames/<name>.sav).')),
    ('CZaxSaveGameStats', 'Item List'): ('confirmed', '0x5bc2a0, 0x564090', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Save game summary shown on the load/save screen; filled by the game when saving. Statistics lines '
        "(CStatsInventoryItem) of the player's items.")),
    ('CZaxSaveGameStats', 'Save Game Name'): ('confirmed', '0x5bc810, 0x5bc910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Name pattern of the save: \\l stands for the map name, \\m for "M" plus the mission number, \\\\ for a '
        'backslash (default "\\m \\l").')),
    ('SyfaceTypeSoundItem', 'Surface Type'): ('confirmed', '0x4c0950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Surface type (default "Generic") for which this entry\'s sound is played; the action looks up the surface'
        ' under the target and uses the first entry that matches.')),
    ('SyfaceTypeSoundItem', 'Sound'): ('confirmed', '0x4c0950', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Sound played on that surface type instead of the action\'s "Default Sound".')),
}

# (registering class, field): (kind, evidence, addresses, English note)
CORRECTIONS: dict[tuple[str, str], tuple[str, str, str, str]] = {
    ('CFireContinuousFireWeaponBaseAI', 'Score Every'): ('misleading', 'confirmed', '0x4737c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Not a frequency: on every update the accuracy statistic gets the frame time multiplied by this value as '
        'shots (and as hits while the beam damages something), so it only weights continuous fire against single '
        'shots in the accuracy ratio.')),
    ('CBroadcastEvilAI', 'Evil To Broadcast'): ('incomplete', 'confirmed', '0x585140, 0x584d40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The amount is sent every frame regardless of frame time and only reaches Sphere of Zin items in the same'
        ' layer, scaled down by the squared distance.')),
    ('CPickupAI', 'Alternate Item Def'): ('incomplete', 'confirmed', '0x53e110, 0x53dea0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is given whenever the item refuses the character for any reason (its acceptance test fails), not only'
        ' when the character already has it; if both refuse, the character cannot touch the pickup at all.')),
    ('CSkeletonAI', 'Respond to calls for reinforcements'): ('incomplete', 'confirmed', '0x5762e0, 0x55d070', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The call reaches active objects within the action\'s "Max Distance" that share a category with the '
        "caller. A character answers only while it is patrolling, only if the caller's target is one of its own "
        'target categories and not too far from its home.')),
    ('CBeginNonInteractiveSequenceAction', 'Scene List'): ('incomplete', 'confirmed', '0x521ef0, 0x522110, 0x5222a0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Each scene names the object the camera moves to, its own camera speed and an action run when the camera '
        'arrives. The next scene starts only when a CEndCurrentNonInteractiveSequenceSceneAction ends the current'
        ' one; after the last one the view goes back to the player.')),
    ('CBroadcastMessageToAreaAction', 'Radius'): ('incomplete', 'confirmed', '0x4c6aa0, 0x4fb910', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The area is a rectangle, not a circle: "Radius" pixels to each side of the object\'s centre and "Radius" '
        'times 0.713 up and down; only active objects in it receive the message.')),
    ('CCreateLayerPartAction', 'Copy Height'): ('incomplete', 'confirmed', '0x4bc230, 0x4bc1c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The height is taken only from a location that is an entity; a location that is no entity, or no location'
        ' at all combined with a "Random Location Delta", sets the new entity\'s height to 0 when this box is '
        'checked.')),
    ('CGameTypeSpecificAction', 'Actions'): ('incomplete', 'confirmed', '0x5a89d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The list is indexed by the position of the current game type in the game type list (one entry per type, '
        'in that order); if the list has no entry for the current type, or none is selected, nothing runs and the'
        ' action fails.')),
    ('CGiveTeamAPointAction', 'Team Number'): ('wrong', 'confirmed', '0x5a9950, 0x51bb90', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In the code the number is the 0-based team index: 0 is the blue team and 1 the red team (the multiplayer'
        ' teams are named and coloured in that order); 1 = Blue, 2 = Red is off by one.')),
    ('CIsOnTeamAction', 'Team Number'): ('wrong', 'confirmed', '0x5a8d70', QT_TRANSLATE_NOOP(
        'fieldhelp', 'In the code the number is the 0-based team index: 0 is the blue team and 1 the red team (the multiplayer'
        ' teams are named and coloured in that order); 1 = Blue, 2 = Red is off by one.')),
    ('CSayQuip', 'Probablity Of Saying Quip'): ('incomplete', 'confirmed', '0x55b050', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The percentage is cut to a whole number and compared with a random number from 0 to 100, so the chance '
        'is (p + 1) / 101: 0 % still says the quip about 1 time in 101, 100 % always. The category\'s "Condition" '
        'action must succeed first.')),
    ('CMultiPlayerGameType', 'Max Number of Teams'): ('incomplete', 'confirmed', '0x51c010, 0x51bef0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only read in team games ("Is Team Game" = 1); otherwise it is ignored. "Unlimited" (0) lets the team '
        'assignment use up to 20 teams.')),
    ('CCaptureTheFlagGameType', 'Points For Killing Self'): ('incomplete', 'confirmed', '0x469800', QT_TRANSLATE_NOOP(
        'fieldhelp', 'These points also go to a player who dies without a killing player (for example by a monster or the '
        'level), not only on suicide.')),
    ('CHudBarOptions', 'MiniMap Background Color'): ('incomplete', 'confirmed', '0x59fe70, 0x4ed150, 0x51cba0', QT_TRANSLATE_NOOP(
        'fieldhelp', "Besides being the unexplored (fog) colour it is also the background of the layer's mini-map image and, "
        'in multiplayer, of the mini score board.')),
    ('CHudBarOptions', 'Fog Of War Update Distance'): ('misleading', 'confirmed', '0x508000', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is a squared distance in pixels² (4096 = 64 pixels), and -1 means update every frame.')),
    ('CInventoryDisplayPageOptions', 'Detail Image Width'): ('misleading', 'confirmed', '0x4d85d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The value is stored but not used: the detail picture is drawn at the picture's own size.")),
    ('CInventoryDisplayPageOptions', 'Detail Image Height'): ('misleading', 'confirmed', '0x4d85d0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The value is stored but not used: the detail picture is drawn at the picture's own size.")),
    ('CInventoryDisplayPageOptions', 'Detail Stats X'): ('incomplete', 'confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', "It is the position of the item's name; the statistics are drawn 1.5 name-font lines below it.")),
    ('CInventoryDisplayPageOptions', 'Detail Stats Y'): ('incomplete', 'confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', "It is the y of the item's name; the statistics are drawn 1.5 name-font lines below it.")),
    ('CInventoryDisplayPageOptions', 'Detail Stats Width'): ('incomplete', 'confirmed', '0x4dbd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'Only the description text uses it, as its wrapping width (minus both margins); the statistics are not '
        'limited by it.')),
    ('CInventoryDisplayPageOptions', 'Detail Stats Height'): ('misleading', 'confirmed', '0x4d85d0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is stored but not used; the statistics area has no height limit.')),
    ('CLayerPart', 'Team Number'): ('incomplete', 'confirmed', '0x4fa960, 0x4f4950, 0x544cf0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The number is 0-based (0-15) with -1 "Nutral" as default; it selects the spawn entry in the level\'s Team'
        ' Info and is compared by team actions and the friendly-fire test. Which colour a team shows was not seen'
        ' in the code read.')),
    ('CEntityOm', 'Angle Of Allowed Collisions'): ('incomplete', 'confirmed', '0x526420, 0x526550', QT_TRANSLATE_NOOP(
        'fieldhelp', "The angle is an offset from Om's current facing angle (radians, shown in degrees): a collision counts as"
        " an eye hit when the direction from Om's position to the contact point minus this value lies within "
        'Angle Plus Or Minus of the facing angle. Only such collision damage gets through; all other damage to Om'
        ' is set to 0.')),
    ('CLayerSaveData', 'Left Mini-Map Clipping'): ('misleading', 'confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is in level (world) pixels, not mini-map pixels, and nothing is masked: the level area is '
        'cropped by it at the left edge and the rest is scaled to fit the mini map (keeping its aspect) and '
        'centred. It takes effect when the mini-map mapping is computed, which the game does at the start of a '
        'level.')),
    ('CLayerSaveData', 'Top Mini-Map Clipping'): ('misleading', 'confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is in level (world) pixels, not mini-map pixels, and nothing is masked: the level area is '
        'cropped by it at the top edge and the rest is scaled to fit the mini map (keeping its aspect) and '
        'centred. It takes effect when the mini-map mapping is computed, which the game does at the start of a '
        'level.')),
    ('CLayerSaveData', 'Right Mini-Map Clipping'): ('misleading', 'confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is in level (world) pixels, not mini-map pixels, and nothing is masked: the level area is '
        'cropped by it at the right edge and the rest is scaled to fit the mini map (keeping its aspect) and '
        'centred. It takes effect when the mini-map mapping is computed, which the game does at the start of a '
        'level.')),
    ('CLayerSaveData', 'Bottom Mini-Map Clipping'): ('misleading', 'confirmed', '0x4ec280, 0x4ec3c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is in level (world) pixels, not mini-map pixels, and nothing is masked: the level area is '
        'cropped by it at the bottom edge and the rest is scaled to fit the mini map (keeping its aspect) and '
        'centred. It takes effect when the mini-map mapping is computed, which the game does at the start of a '
        'level.')),
    ('CMissionDisplayPageOptions', 'Mission Title Area Width'): ('misleading', 'confirmed', '0x510590', QT_TRANSLATE_NOOP(
        'fieldhelp', 'No code reads this width: the mission title is neither clipped nor centred to it.')),
    ('CMissionObjectiveDisplayOptions', 'Mission Detail Font'): ('incomplete', 'confirmed', '0x509910', QT_TRANSLATE_NOOP(
        'fieldhelp', "Besides the mission's description it is also the font of every objective's description (the label before"
        ' its status).')),
    ('CMissionOverWindowOptions', 'Close Button Pressed Frame'): ('wrong', 'confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', "This is the close button's pressed image: it is drawn only while the button is pressed (and sets the "
        'button\'s size). The disabled look comes from "Close Button Disabed Frame".')),
    ('CMissionOverWindowOptions', 'Close Button Disabed Frame'): ('wrong', 'confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', "This is the close button's disabled image, drawn while the button is disabled (in the mission failed "
        'window); the pressed look comes from "Close Button Pressed Frame".')),
    ('CMissionOverWindowOptions', 'Failed Title Text'): ('wrong', 'confirmed', '0x50cab0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'This is the title of the window shown when a mission is failed, not completed.')),
    ('CNonInteractiveSequenceScene', 'Camera Speed'): ('incomplete', 'confirmed', '0x521ef0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is in pixels per second; 0 ("Immediately") jumps the camera to the target without moving.')),
    ('CQuestStat', 'Hide This Stat'): ('incomplete', 'confirmed', '0x554b80, 0x5527f0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The row is not shown, but its point value is still added to the mission's total score.")),
    ('CQuestCounterData', 'Cumulative Par Score'): ('misleading', 'confirmed', '0x554fd0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is the sum of the par scores of all previous missions, not only of the last one.')),
    ('CQuestFloatAccumulatorData', 'Cumulative Par Score'): ('misleading', 'confirmed', '0x556c30', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is the sum of the par scores of all previous missions, not only of the last one.')),
    ('CQuestPercentageData', 'Cumulative Par Numerator'): ('misleading', 'confirmed', '0x55a100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is the sum of the par numerators of all previous missions, not only of the last one.')),
    ('CQuestPercentageData', 'Cumulative Par Denominator'): ('misleading', 'confirmed', '0x55a100', QT_TRANSLATE_NOOP(
        'fieldhelp', 'It is the sum of the par denominators of all previous missions, not only of the last one.')),
    ('CQuipCategory', 'Minimum Time Between Saying'): ('incomplete', 'confirmed', '0x55b770, 0x55b730, 0x55bd50', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The wait starts when the quip is triggered (not when it is said) and is restarted by a re-trigger while '
        'the quip is pending; a trigger that loses the "Say Quip" probability roll also starts the wait when it '
        'had run out.')),
    ('CSphereOfZinOptions', 'Evil Unit Lenght'): ('incomplete', 'confirmed', '0x584d40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The value is a squared distance (pixels²): evil broadcast at distance d charges the sphere by amount × '
        'value / d² of what is missing to full, so at d² = value the full amount applies and it falls off with '
        'the square of the distance.')),
    ('CSphereOfZinOptions', 'Apply Ceiling Prematurely'): ('incomplete', 'confirmed', '0x584d40', QT_TRANSLATE_NOOP(
        'fieldhelp', 'When set, sources closer than "Evil Unit Lenght" count as if at that distance, so a single broadcast '
        'never adds more than its amount; when cleared, nearby sources can add far more (the charge is only '
        'capped at full afterwards, and a source at distance 0 divides by zero).')),
    ('CThresholdTrigger', 'Re-Trigger Amount'): ('incomplete', 'confirmed', '0x584980', QT_TRANSLATE_NOOP(
        'fieldhelp', 'After firing, the trigger is re-armed once the value is at least this far from the threshold on either '
        'side; it then fires again on the next crossing in its direction.')),
    ('CVoiceLogDisplayPageOptions', 'Column Header Font'): ('wrong', 'confirmed', '0x5948b0, 0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The voice log page never reads this value; the column header is drawn in its default font.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Width'): ('wrong', 'confirmed', '0x5948b0, 0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The voice log page never reads this value; the button takes its size from its "Replay" image.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Height'): ('wrong', 'confirmed', '0x5948b0, 0x5950c0', QT_TRANSLATE_NOOP(
        'fieldhelp', 'The voice log page never reads this value; the button takes its size from its "Replay" image.')),
    ('CVoiceLogDisplayPageOptions', 'Replay Button Font'): ('wrong', 'confirmed', '0x5948b0', QT_TRANSLATE_NOOP(
        'fieldhelp', "The voice log page never reads this value; the button's text uses the button's default font.")),
}


EVIDENCE = {'confirmed': QT_TRANSLATE_NOOP('fieldhelp', 'confirmed'),
            'verified': QT_TRANSLATE_NOOP('fieldhelp', 'verified'),
            'assumption': QT_TRANSLATE_NOOP('fieldhelp', 'assumption')}
CHECK = {'wrong': QT_TRANSLATE_NOOP('fieldhelp', 'The help text above is wrong'),
         'incomplete': QT_TRANSLATE_NOOP('fieldhelp', 'The help text above is incomplete'),
         'misleading': QT_TRANSLATE_NOOP('fieldhelp', 'The help text above is misleading')}


def _source(evidence: str, addrs: str) -> str:
    ev = translate('fieldhelp', EVIDENCE.get(evidence, evidence))
    return f'{ev}, {addrs}' if addrs else ev


def help_text(owner: str, key: str) -> str | None:
    """Our help text of field ``key`` registered by class ``owner``, translated and marked as derived from
    the game code; None without one."""
    h = HELP.get((owner, key))
    if not h:
        return None
    return translate('fieldhelp', 'From the game code ({source}):').format(source=_source(h[0], h[1])) + ' ' + \
        translate('fieldhelp', h[2])


def correction_text(owner: str, key: str) -> str | None:
    """Our note on the exe's help text of field ``key`` of ``owner`` where the code contradicts it, followed
    by our help text of the field if it has one (one source line for both); None without a note."""
    c = CORRECTIONS.get((owner, key))
    if not c:
        return None
    h = HELP.get((owner, key))
    addrs = ', '.join(dict.fromkeys(a for a in (c[2] + ', ' + h[1] if h else c[2]).split(', ') if a))
    what = translate('fieldhelp', CHECK.get(c[0], CHECK['incomplete']))
    text = translate('fieldhelp', c[3]) + (' ' + translate('fieldhelp', h[2]) if h else '')
    return translate('fieldhelp', '{what} (game code: {source}):').format(what=what, source=_source(c[1], addrs)) + \
        ' ' + text
