#!/usr/bin/env python3
"""
Gym Equipment Analyzer v3
Backend: Flask + Ollama vision + curated exercise DB
- Aggressive multi-pass vision (3 prompts) to extract ALL equipment
- Fallback chain: vision → keyword matching → context inference
- Always returns exercises from curated DB, never LLM (accuracy)
- Fully responsive frontend (mobile + tablet + desktop)
"""

import os, json, base64, re, requests
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
UPLOAD_DIR = Path('/opt/hermes/gym-analyzer/uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

# Cloud vision via Ollama Cloud API (gemma3:12b — good vision, fast)
OLLAMA_CLOUD_KEY = ""
try:
    with open('/opt/data/.env') as f:
        for line in f:
            if 'OLLAMA_API_KEY' in line:
                OLLAMA_CLOUD_KEY = line.split('=')[1].strip().strip('"').strip("'")
                break
except: pass

CLOUD_VISION_MODEL = "gemma3:12b"

# ─────────────────────────────── EXERCISE DB ──────────────────────────────
EXERCISE_DB = {
    "dumbbell": {"name": "Dumbbell", "category": "free_weight",
        "primary_muscles": ["Biceps", "Triceps", "Shoulders", "Chest", "Back"],
        "common_exercises": [
            {"name":"Dumbbell Bicep Curl","video_id":"20ibpB635Rw","muscles_worked":["Biceps Brachii","Brachialis","Forearm Flexors"],
             "steps":["Stand upright holding a dumbbell in each hand, palms facing forward.","Keep elbows close to your torso, upper arms stationary.","Curl the weights up while contracting your biceps.","Continue until dumbbells are at shoulder level.","Slowly lower back to the starting position."],
             "common_mistakes":["Swinging weights with momentum","Moving elbows forward"],"safety_tips":["Use controlled motion, not momentum","Don't arch your back"]},
            {"name":"Dumbbell Shoulder Press","video_id":"xtsbSAgNBpI","muscles_worked":["Anterior Deltoid","Lateral Deltoid","Triceps"],
             "steps":["Sit on a bench with back support, dumbbells at shoulder height.","Palms face forward, elbows bent at 90 degrees.","Press dumbbells upward until arms are extended.","Pause at the top, then lower back to shoulder height."],
             "common_mistakes":["Flaring elbows too wide","Leaning back excessively"],"safety_tips":["Keep your core braced","Don't lock elbows at the top"]},
            {"name":"Dumbbell Chest Press","video_id":"z6A4W5Dib28","muscles_worked":["Pectoralis Major","Anterior Deltoid","Triceps"],
             "steps":["Lie on a flat bench with a dumbbell in each hand at chest level.","Press the dumbbells upward until arms are extended.","Lower slowly until elbows are below the bench line."],
             "common_mistakes":["Bouncing dumbbells off the chest","Uneven pressing"],"safety_tips":["Use a spotter for heavy weights","Control the descent"]},
            {"name":"Dumbbell Row","video_id":"OL8yGrkXyiQ","muscles_worked":["Latissimus Dorsi","Rhomboids","Trapezius","Biceps"],
             "steps":["Place one knee and hand on a bench for support.","Hold a dumbbell in the other hand, arm extended.","Pull the dumbbell toward your hip, squeezing your back.","Lower with control."],
             "common_mistakes":["Rotating the torso","Using too much arm"],"safety_tips":["Keep your back flat","Don't jerk the weight"]}]},
    "barbell": {"name":"Barbell","category":"free_weight",
        "primary_muscles":["Chest","Back","Legs (Quadriceps, Hamstrings, Glutes)","Shoulders"],
        "common_exercises":[
            {"name":"Barbell Bench Press","video_id":"0cXAp6WhSj4","muscles_worked":["Pectoralis Major","Anterior Deltoid","Triceps Brachii"],
             "steps":["Lie flat, feet planted, grip bar slightly wider than shoulder-width.","Unrack and hold directly above shoulders.","Lower to mid-chest with elbows at ~75 degrees.","Press back up explosively.","Lock out elbows without overextending."],
             "common_mistakes":["Bouncing bar off chest","Uneven grip"],"safety_tips":["Always use a spotter","Keep wrists straight"]},
            {"name":"Barbell Squat","video_id":"iZTxa8NJH2g","muscles_worked":["Quadriceps","Hamstrings","Gluteus Maximus","Erector Spinae"],
             "steps":["Position bar on upper back, grip evenly.","Unrack, step back feet shoulder-width, toes slightly out.","Brace core, push hips back, bend knees to lower.","Descend until thighs parallel or deeper.","Drive through heels to stand up."],
             "common_mistakes":["Knees caving inward","Rounding lower back"],"safety_tips":["Use a squat rack with safety bars","Keep chest up"]},
            {"name":"Barbell Deadlift","video_id":"8np3vKDBJfc","muscles_worked":["Erector Spinae","Glutes","Hamstrings","Traps","Forearms"],
             "steps":["Stand feet hip-width, bar over mid-foot.","Hinge at hips, grip bar just outside shins.","Flatten back, brace core, chest up.","Drive through heels, keep bar close to body.","Stand tall, then control bar back down."],
             "common_mistakes":["Rounding lower back","Jerking bar off floor"],"safety_tips":["Use mixed grip for heavy weight","Form first — never ego lift"]}]},
    "kettlebell": {"name":"Kettlebell","category":"free_weight",
        "primary_muscles":["Glutes","Hamstrings","Core","Shoulders","Back"],
        "common_exercises":[
            {"name":"Kettlebell Swing","video_id":"gAJMf7Nv4N0","muscles_worked":["Glutes","Hamstrings","Erector Spinae","Core","Deltoids"],
             "steps":["Stand with feet wider than shoulder-width, kettlebell on floor.","Hinge at hips, back flat, grip handle with both hands.","Hike kettlebell between legs like a football snap.","Explosively drive hips forward to swing bell to chest height.","Let bell drop back, hinging for the next rep."],
             "common_mistakes":["Squatting instead of hip-hinging","Using arms to lift"],"safety_tips":["Power comes from hips, not shoulders","Keep wrists straight"]}]},
    "resistance band": {"name":"Resistance Band","category":"free_weight",
        "primary_muscles":["Shoulders","Arms","Back","Glutes","Core"],
        "common_exercises":[
            {"name":"Band Rows","video_id":"LSkyinhmA8k","muscles_worked":["Rhomboids","Latissimus Dorsi","Biceps"],
             "steps":["Anchor band at chest height or step on it.","Grip band, pull toward torso, squeeze shoulder blades.","Slowly release with control."],
             "common_mistakes":["Using momentum","Not fully extending"],"safety_tips":["Check band for tears before use","Don't overstretch beyond 3x resting length"]}]},
    "bench": {"name":"Weight Bench","category":"free_weight",
        "primary_muscles":["Chest","Shoulders","Core","Back"],
        "common_exercises":[
            {"name":"Bench Press","video_id":"0cXAp6WhSj4","muscles_worked":["Pectoralis Major","Anterior Deltoid","Triceps"],
             "steps":["Lie back on bench, feet flat on floor.","Grip weight(s) at chest level.","Press up until arms extended.","Lower with control to chest level."],
             "common_mistakes":["Wrong bench angle for target muscle","Bouncing"],"safety_tips":["Use a spotter for heavy loads","Adjust bench angle for incline/decline"]},
            {"name":"Dumbbell Row","video_id":"OL8yGrkXyiQ","muscles_worked":["Latissimus Dorsi","Rhomboids","Trapezius","Biceps"],
             "steps":["Place one knee and hand on bench.","Hold dumbbell, arm extended.","Pull toward hip, squeezing back.","Lower with control."],
             "common_mistakes":["Rotating torso","Using too much arm"],"safety_tips":["Keep back flat","Don't jerk the weight"]}]},
    "cable machine": {"name":"Cable Machine","category":"cable",
        "primary_muscles":["Chest","Back","Shoulders","Arms","Core"],
        "common_exercises":[
            {"name":"Cable Chest Fly","video_id":"I-Ue34qLxc4","muscles_worked":["Pectoralis Major","Anterior Deltoid"],
             "steps":["Set pulleys to chest height, grab handles.","Stand centered between pulleys, step forward slightly.","With slight bend in elbows, bring hands together.","Slowly open arms back."],
             "common_mistakes":["Too much weight compromising form","Bending elbows too much"],"safety_tips":["Start light to feel the movement","Control the eccentric phase"]},
            {"name":"Cable Tricep Pushdown","video_id":"1FjkhpZsaxc","muscles_worked":["Triceps Brachii"],
             "steps":["Attach bar/rope to high pulley.","Grip at shoulder width, elbows pinned to sides.","Push bar down until arms extended.","Slowly return to 90 degrees."],
             "common_mistakes":["Elbows flaring outward","Using body momentum"],"safety_tips":["Keep torso still","Don't let weight stack touch between reps"]}]},
    "smith machine": {"name":"Smith Machine","category":"machine",
        "primary_muscles":["Chest","Shoulders","Legs (Quadriceps, Glutes)"],
        "common_exercises":[
            {"name":"Smith Machine Squat","video_id":"iKCJCydYYrE","muscles_worked":["Quadriceps","Glutes","Hamstrings"],
             "steps":["Position bar on traps, grip wide.","Unrack by rotating bar, step forward.","Squat keeping torso upright, knees tracking toes.","Drive through heels to stand.","Rerack by rotating bar back."],
             "common_mistakes":["Bar too low on back (neck pressure)","Knees past toes excessively"],"safety_tips":["Check safety stops","Control is still on you despite guided track"]}]},
    "leg press machine": {"name":"Leg Press Machine","category":"machine",
        "primary_muscles":["Quadriceps","Hamstrings","Glutes","Calves"],
        "common_exercises":[
            {"name":"Leg Press","video_id":"nDh_BlnLCGc","muscles_worked":["Quadriceps","Gluteus Maximus","Hamstrings","Gastrocnemius"],
             "steps":["Sit with back and head flat against pad.","Place feet shoulder-width on platform, toes slightly out.","Grip side handles, release safety levers.","Lower platform until knees at ~90 degrees.","Drive through heels to push back up without locking knees."],
             "common_mistakes":["Going too deep (butt lifting off seat)","Locking knees at top"],"safety_tips":["Never fully lock knees","Keep butt planted on seat"]}]},
    "weight machine": {"name":"Weight Machine / Multi-Gym","category":"machine",
        "primary_muscles":["Chest","Back","Shoulders","Arms","Legs (full body)"],
        "common_exercises":[
            {"name":"Lat Pulldown","video_id":"OEXosPwzFdc","muscles_worked":["Latissimus Dorsi","Biceps Brachii","Rhomboids"],
             "steps":["Sit facing machine, adjust thigh pad.","Grip bar wider than shoulder-width, palms away.","Pull bar down to upper chest, squeezing shoulder blades.","Slowly return to starting position."],
             "common_mistakes":["Using momentum to swing","Pulling bar behind neck"],"safety_tips":["Keep chest up and back straight","Don't lean back excessively"]},
            {"name":"Seated Cable Row","video_id":"LSkyinhmA8k","muscles_worked":["Rhomboids","Latissimus Dorsi","Biceps","Rear Deltoids"],
             "steps":["Sit on bench, feet on platform, knees slightly bent.","Grip handle with arms extended.","Pull toward torso, squeezing shoulder blades.","Slowly extend arms back."],
             "common_mistakes":["Rounding lower back","Using arm strength instead of back"],"safety_tips":["Keep back straight","Control the eccentric phase"]},
            {"name":"Chest Press Machine","video_id":"0cXAp6WhSj4","muscles_worked":["Pectoralis Major","Anterior Deltoid","Triceps"],
             "steps":["Adjust seat so handles at mid-chest level.","Grip handles and press forward until arms extended.","Slowly return."],
             "common_mistakes":["Too much weight compromising form","Not full range of motion"],"safety_tips":["Keep back flat against pad","Exhale on press, inhale on return"]}]},
    "rowing machine": {"name":"Rowing Machine","category":"cardio",
        "primary_muscles":["Back (Lats, Rhomboids)","Legs (Quadriceps, Hamstrings)","Core","Arms"],
        "common_exercises":[
            {"name":"Indoor Rowing","video_id":"OL8yGrkXyiQ","muscles_worked":["Latissimus Dorsi","Rhomboids","Quadriceps","Hamstrings","Core","Biceps"],
             "steps":["Sit on seat, strap feet in, grip handle.","Start with knees bent, arms extended (catch position).","Drive through legs first, lean back, pull handle to lower ribs.","Extend arms first, lean forward, bend knees to slide back.","Repeat: legs → body → arms, arms → body → legs."],
             "common_mistakes":["Bending arms too early","Rounding lower back"],"safety_tips":["60% legs, 20% core, 20% arms","Keep straight back, engage core"]}]},
    "pull up bar": {"name":"Pull-Up Bar","category":"bodyweight",
        "primary_muscles":["Back (Lats)","Biceps","Shoulders","Core"],
        "common_exercises":[
            {"name":"Pull-Up","video_id":"OEXosPwzFdc","muscles_worked":["Latissimus Dorsi","Biceps Brachii","Rhomboids","Traps"],
             "steps":["Grip bar palms away, slightly wider than shoulder-width.","Hang with arms extended, engage core.","Pull up until chin clears bar.","Lower with control to full hang."],
             "common_mistakes":["Excessive kipping","Not going to full extension"],"safety_tips":["Control the negative phase","Use a spotter band if needed"]},
            {"name":"Chin-Up","video_id":"Ln3gAdHr8MM","muscles_worked":["Biceps Brachii","Latissimus Dorsi","Brachoradialis"],
             "steps":["Grip bar palms toward you, shoulder-width.","Hang fully, pull up until chin clears bar.","Lower with control to full extension."],
             "common_mistakes":["Using momentum","Partial reps"],"safety_tips":["Breathe out on the way up","Keep legs still"]}]},
    "yoga mat": {"name":"Yoga Mat / Exercise Mat","category":"bodyweight",
        "primary_muscles":["Core","Legs","Glutes","Arms (full body)"],
        "common_exercises":[
            {"name":"Plank","video_id":"pvIjsG5Svck","muscles_worked":["Rectus Abdominis","Transverse Abdominis","Shoulders","Glutes"],
             "steps":["Start on hands and knees, hands under shoulders.","Step feet back into straight line head to heels.","Engage core, glutes, keep back flat.","Hold position, breathe steadily."],
             "common_mistakes":["Hips sagging or piking up","Holding breath"],"safety_tips":["Look at floor, not forward","Start with 20-30 second holds"]},
            {"name":"Push-Up","video_id":"I9fsqKE5XHo","muscles_worked":["Pectoralis Major","Triceps","Deltoids","Core"],
             "steps":["Start in plank, hands wider than shoulders.","Lower body until chest nearly touches floor.","Keep elbows at ~45 degrees from body.","Push back up."],
             "common_mistakes":["Flaring elbows to 90 degrees","Hips dropping"],"safety_tips":["Keep body in straight line","Knee push-ups are valid progressions"]}]},
    "treadmill": {"name":"Treadmill","category":"cardio",
        "primary_muscles":["Legs (Quadriceps, Hamstrings, Calves)","Glutes","Core stabilizers"],
        "common_exercises":[
            {"name":"Treadmill Walking/Running","video_id":"zeS4qu6bXy4","muscles_worked":["Quadriceps","Hamstrings","Gastrocnemius","Soleus","Glutes"],
             "steps":["Step onto sides first, start belt at slow speed.","Begin walking to warm up, gradually increase speed.","Maintain upright posture, look forward.","Swing arms naturally, land mid-foot.","Cool down gradually before stepping off."],
             "common_mistakes":["Holding handrails (reduced calorie burn)","Looking down at feet"],"safety_tips":["Attach safety clip to clothing","Start slow, increase gradually"]}]},
    "exercise bike": {"name":"Exercise Bike","category":"cardio",
        "primary_muscles":["Quadriceps","Hamstrings","Calves","Glutes","Core"],
        "common_exercises":[
            {"name":"Stationary Cycling","video_id":"dieOsJlsvpM","muscles_worked":["Quadriceps","Hamstrings","Gastrocnemius","Soleus","Glutes"],
             "steps":["Adjust seat so leg nearly extended at bottom of pedal stroke.","Position handlebars at comfortable reach.","Start pedaling at low resistance to warm up.","Maintain 70-90 RPM for steady-state cardio.","Stand occasionally for glute activation."],
             "common_mistakes":["Seat too low (knee strain)","Resistance too high (knees grind)"],"safety_tips":["Proper seat height prevents knee injury","Stay hydrated"]}]},
    "elliptical": {"name":"Elliptical Machine","category":"cardio",
        "primary_muscles":["Quadriceps","Hamstrings","Glutes","Core","Arms"],
        "common_exercises":[
            {"name":"Elliptical Training","video_id":"EesEvYohy5o","muscles_worked":["Quadriceps","Hamstrings","Glutes","Upper body"],
             "steps":["Step onto machine, grip handles.","Start pedaling smooth forward motion.","Increase resistance gradually.","Reverse motion for different muscle fibers.","Maintain upright posture, don't lean on console."],
             "common_mistakes":["Leaning heavily on console","Staying at low resistance"],"safety_tips":["Start with no resistance to warm up","Keep natural stride"]}]}
}

EXERCISE_VIDEOS = {ex["name"]: ex["video_id"] for eq in EXERCISE_DB.values() for ex in eq["common_exercises"]}

def enrich_exercises_with_videos(exercises):
    if not exercises:
        return exercises
    KEY_MOVES = {"pull":"Pull-Up","row":"Dumbbell Row","curl":"Dumbbell Bicep Curl","press":"Dumbbell Shoulder Press","fly":"Cable Chest Fly",
                 "swing":"Kettlebell Swing","squat":"Barbell Squat","deadlift":"Barbell Deadlift","plank":"Plank","push":"Push-Up",
                 "chin":"Chin-Up","cycle":"Stationary Cycling","bike":"Stationary Cycling","treadmill":"Treadmill Walking/Running",
                 "elliptical":"Elliptical Training","leg press":"Leg Press","tricep":"Cable Tricep Pushdown","bicep":"Dumbbell Bicep Curl",
                 "band":"Band Rows","chest fly":"Cable Chest Fly","cable row":"Band Rows","lat pulldown":"Pull-Up",
                 "shoulder press":"Dumbbell Shoulder Press","bicep curl":"Dumbbell Bicep Curl","tricep pushdown":"Cable Tricep Pushdown",
                 "lateral raise":"Dumbbell Shoulder Press","leg extension":"Leg Press","leg curl":"Leg Press",
                 "bent over row":"Dumbbell Row","seated row":"Band Rows","chest press":"Bench Press","indoor row":"Indoor Rowing","rowing":"Indoor Rowing"}
    for ex in exercises:
        if ex.get("video_id"): continue
        n = ex.get("name","").strip(); nl = n.lower()
        if n in EXERCISE_VIDEOS: ex["video_id"] = EXERCISE_VIDEOS[n]; continue
        matched = False
        for phrase, target in sorted(KEY_MOVES.items(), key=lambda x: -len(x[0].split())):
            if phrase in nl and target in EXERCISE_VIDEOS: ex["video_id"] = EXERCISE_VIDEOS[target]; matched = True; break
        if matched: continue
        for kn, vid in EXERCISE_VIDEOS.items():
            if nl in kn.lower() or kn.lower() in nl: ex["video_id"] = vid; break
    return exercises

def ollama_vision(image_path, prompt):
    """Vision analysis — tries cloud API first, falls back to local moondream."""
    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')

    # Try cloud vision first (gemma3:12b via Ollama Cloud)
    if OLLAMA_CLOUD_KEY:
        try:
            resp = requests.post("https://ollama.com/v1/chat/completions", json={
                "model": CLOUD_VISION_MODEL, "max_tokens": 300,
                "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]}]
            }, headers={
                "Authorization": f"Bearer {OLLAMA_CLOUD_KEY}",
                "Content-Type": "application/json"
            }, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except: pass

    # Fallback: local moondream
    try:
        resp = requests.post("http://localhost:11434/api/chat", json={
            "model": "moondream", "stream": False,
            "messages": [{"role": "user", "content": prompt, "images": [img_b64]}],
            "options": {"num_predict": 512, "temperature": 0.15}
        }, timeout=90)
        return resp.json().get("message", {}).get("content", "")
    except: return ""

def find_equipment_keywords(description):
    """Extract ALL equipment names from text. Returns deduplicated ordered list."""
    keywords = {
        "dumbbell": ["dumbbell","dumbbells","dumbell","dumbbell set","free weight"],
        "barbell": ["barbell","bar bell","olympic bar","ez bar","barbell setup","barbell rack"],
        "kettlebell": ["kettlebell","kettle bell","kettle bells"],
        "resistance band": ["resistance band","exercise band","resistance tube"],
        "bench": ["bench","weight bench","flat bench","adjustable bench","bench press bench"],
        "cable machine": ["cable","cable machine","pulley","crossover","cable crossover","weight stack"],
        "smith machine": ["smith machine","smith"],
        "leg press machine": ["leg press","leg-press"],
        "weight machine": ["weight machine","multi-gym","multi gym","home gym","weight stack machine","selectorized","plate loaded","squat rack","functional trainer","power rack"],
        "rowing machine": ["rowing machine","rower","ergometer","erg","indoor rower","rowing erg"],
        "pull up bar": ["pull up bar","pull-up bar","chin up bar","chin-up bar","pullup bar"],
        "yoga mat": ["yoga mat","exercise mat","fitness mat","yoga"],
        "exercise bike": ["bike","stationary bike","exercise bike","stationary cycle","spin bike","cycle"],
        "treadmill": ["treadmill","tread mill","running machine","walking machine"],
        "elliptical": ["elliptical","cross trainer","elliptical trainer"],
    }
    dl = description.lower()
    matched = {}
    for equip, words in keywords.items():
        for w in words:
            if w in dl:
                matched[equip] = matched.get(equip, 0) + 1
                break
    return sorted(matched.keys(), key=lambda k: (-matched[k], k))

def build_equipment_result(key, db_entry):
    """Build a standardized result dict for one equipment entry."""
    analysis = {
        "equipment_name": db_entry["name"],
        "category": db_entry["category"],
        "difficulty": "Beginner to Intermediate",
        "primary_muscles": db_entry["primary_muscles"],
        "exercises": list(db_entry.get("common_exercises", [])),
        "safety_warnings": ["Always warm up before using this equipment","Start with light weight to practice form","Consult a trainer if unsure about technique"]
    }
    enrich_exercises_with_videos(analysis["exercises"])
    return {"key": key, "name": db_entry["name"], "category": db_entry["category"], "analysis": analysis}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400
    img_path = UPLOAD_DIR / 'current.jpg'
    file.save(str(img_path))

    # Step 1: Multi-pass vision — try 3 different prompts
    descriptions = []
    prompts = [
        "List EVERY piece of gym equipment you can see in this image. Name each one. Be specific and thorough. Look for: dumbbells, barbells, benches, machines, cables, kettlebells, bands, bikes, treadmills, pull-up bars, rowing machines, mats, weight stacks.",
        "What gym equipment is visible? Identify all equipment items one by one.",
        "Describe this scene. What fitness equipment do you see? List all machines, weights, benches, and accessories."
    ]
    for prompt in prompts:
        desc = ollama_vision(str(img_path), prompt)
        if desc and len(desc) > 10:
            descriptions.append(desc)
    full_description = " ".join(descriptions) if descriptions else "Gym scene with various fitness equipment"

    # Step 2: Keyword extraction from ALL descriptions
    all_matched = set()
    for desc in descriptions:
        all_matched.update(find_equipment_keywords(desc))
    matched_keys = sorted(all_matched) if all_matched else find_equipment_keywords(full_description)

    # Step 3: For each matched equipment, return DB data
    results = []
    processed = set()
    for key in matched_keys:
        if key not in EXERCISE_DB or key in processed:
            continue
        processed.add(key)
        results.append(build_equipment_result(key, EXERCISE_DB[key]))

    # Step 4: If vision was weak (<3 items), try a second opinion prompt
    if len(results) <= 2 and len(descriptions) <= 2:
        retry_prompt = "Look again carefully. Besides what you already mentioned, what OTHER gym equipment can you see? Look for: weight bench, barbells, dumbbells, cable machine, kettlebells, pull-up bar, treadmill, exercise bike, mats, bands, rowing machine, smith machine, leg press, multi-gym."
        retry = ollama_vision(str(img_path), retry_prompt)
        if retry and len(retry) > 10:
            more_keys = find_equipment_keywords(retry)
            for key in more_keys:
                if key in EXERCISE_DB and key not in processed:
                    processed.add(key)
                    results.append(build_equipment_result(key, EXERCISE_DB[key]))
                    descriptions.append(retry)

    return jsonify({
        "vision_description": full_description[:600],
        "matched_equipment": list(processed),
        "results": results,
        "equipment_count": len(results)
    })

@app.route('/equipment-list')
def equipment_list():
    names = [{"key":k,"name":v["name"],"category":v["category"]} for k,v in EXERCISE_DB.items()]
    return jsonify(sorted(names, key=lambda x: x["name"]))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    print(f"🏋️ Gym Analyzer v3 starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
