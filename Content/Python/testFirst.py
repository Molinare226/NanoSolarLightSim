import unreal

ELL = unreal.EditorLevelLibrary()
EAL = unreal.EditorAssetLibrary()

FPS = 30
VIDEO_SECONDS = 15
TOTAL_FRAMES = FPS * VIDEO_SECONDS

RENDER_TIMES = [
    (8, 0),
    (10, 0),
    (12, 0),
    (14, 0),
    (16, 0),
]

RENDER_ROOT = (
    "D:/Epic Games/NanoSolarLightSim/"
    "Saved/SolarBenchRenders"
)

def make_location_id(la, lo):
    lat_direction = "S" if la < 0 else "N"
    lon_direction = "E" if lo >= 0 else "W"

    lat_text = f"{abs(la):.6f}".replace(".", "_")
    lon_text = f"{abs(lo):.6f}".replace(".", "_")

    return (
        f"{lat_direction}{lat_text}_"
        f"{lon_direction}{lon_text}"
    )

_render_index = 0
_render_sequence_path = None
_render_location_id = None

_active_capture = None
_active_callback = None

def test():
    print("hello")
    
def testGIS():

    subsystem = unreal.get_editor_subsystem(
        unreal.EditorActorSubsystem
    )

    geo = None

    for actor in subsystem.get_all_level_actors():
        if actor.get_class().get_name()=="GeoReferencingSystem":
            geo = actor
            break

    if geo is None:
        print("No GeoReference found")
        return

    print(geo)

    gps = unreal.GeographicCoordinates()
    
    gps.latitude = -33.890261
    gps.longitude = 151.192769
    gps.altitude = 20

    world_pos = geo.geographic_to_engine(gps)

    print(world_pos)
    
def getGroundZ(location):

    start = unreal.Vector(
        location.x,
        location.y,
        100000
    )

    end = unreal.Vector(
        location.x,
        location.y,
        -100000
    )

    hit = unreal.SystemLibrary.line_trace_single(
        ELL.get_editor_world(),
        start,
        end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        False,
        [],
        unreal.DrawDebugTrace.FOR_DURATION
    )

    data = hit.to_dict()

    print(data)

    if data["blocking_hit"]:
        point = data["location"]
        print("Ground point:", point)
        return point.z

    print("No ground detected")
    return location.z
    
def spawn(la, lo):

    actors = unreal.get_editor_subsystem(
        unreal.EditorActorSubsystem
    ).get_all_level_actors()

    geo = None
    
    for actor in actors:
        if actor.get_class().get_name()=="GeoReferencingSystem":
            geo = actor
            break
        
    if geo is None:
            unreal.log_error(
                "GeoReferencingSystem was not found."
            )
            return None
    
    location_id = make_location_id(la, lo)
    actor_label = f"SolarBench_{location_id}"
    
    for actor in actors:
        if actor.get_actor_label() == actor_label:
            unreal.log_warning(
                f"Using existing target: {actor_label}"
            )
            return actor
    
    gps = unreal.GeographicCoordinates()
    gps.latitude = la
    gps.longitude = lo
    gps.altitude = 20.0


    pos = geo.geographic_to_engine(gps)
    
    ground_z = getGroundZ(pos)

    pos.z = ground_z

    benchPath = EAL.load_asset("/Game/Meshes/SM_MERGED_StaticMeshActor_8")
    if benchPath is None:
        unreal.log_error(
            "Solar bench asset could not be loaded."
        )
        return None

    actor = ELL.spawn_actor_from_object(
        benchPath,
        pos,
        unreal.Rotator()
    )
    if actor is None:
        unreal.log_error(
            "Solar bench could not be spawned."
        )
        return None
    
    actor.tags.append(unreal.Name("synthetic_target"))
    actor.set_actor_label(actor_label)
    
    snap_to_landscape(actor)
    
    unreal.log(
        f"Spawned {actor.get_actor_label()} at "
        f"{actor.get_actor_location()}"
    )
    
    return actor
    
def snap_to_landscape(actor):

    loc = actor.get_actor_location()

    start = unreal.Vector(
        loc.x,
        loc.y,
        loc.z + 10000
    )

    end = unreal.Vector(
        loc.x,
        loc.y,
        loc.z - 10000
    )

    hit = unreal.SystemLibrary.line_trace_single(
        ELL.get_editor_world(),
        start,
        end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        False,
        [actor],
        unreal.DrawDebugTrace.FOR_DURATION
    )

    data = hit.to_dict()

    if data["blocking_hit"]:

        ground_z = data["location"].z

        bounds = actor.get_actor_bounds(False)

        bottom_z = loc.z - bounds[1].z

        offset = ground_z - bottom_z

        new_loc = unreal.Vector(
            loc.x,
            loc.y,
            loc.z + offset
        )

        actor.set_actor_location(
            new_loc,
            False,
            True
        )

        print(
            actor.get_name(),
            "moved to",
            new_loc
        )

    else:
        print(
            actor.get_name(),
            "no ground hit"
        )

def snap():
    target = unreal.Name("USYD_buildings")
    allActors = ELL.get_all_level_actors()
    validMeshes = []
    
    for actor in allActors:
            if actor.actor_has_tag(target):
                validMeshes.append(actor)
                
    for mesh in validMeshes:
        snap_to_landscape(mesh)

# spawn solar bench mesh  
# def spawnSB(la, lo):
    # quinnPath = EAL.load_asset("/Game/Meshes/SM_MERGED_StaticMeshActor_8")
    
    
    
    # location = unreal.Vector(0.0, 0.0, 280.0)
    # rotation = unreal.Rotator(0.0, 0.0, 190.0)
    # actor = ELL.spawn_actor_from_object(quinnPath, location, rotation)
    # actor.tags.append(unreal.Name("synthetic_target"))
    
# spawn a camera point to the mesh
def spawnCam(target):
    if target is None:
        unreal.log_error(
            "spawnCam received no target."
        )
        return None
    # camera = unreal.CineCameraActor()
    camera_tag = unreal.Name(f"camera_for_{target.get_name()}")
    # target_tag = unreal.Name("synthetic_target")
    
    allActors = ELL.get_all_level_actors()
    
    # validMeshes = []
    cam = None
    
    for actor in allActors:
        # if actor.actor_has_tag(target_tag):
        #    validMeshes.append(actor)
            
        if actor.actor_has_tag(camera_tag):
            cam = actor
            break
            
    bounds_origin, bounds_extent = (
        target.get_actor_bounds(False)
    )
    
    focus_location = (
        bounds_origin
        + unreal.Vector(
            0.0,
            0.0,
            bounds_extent.z * 0.85
        )
    )
    
    footprint_size = max(
        bounds_extent.x,
        bounds_extent.y
    )
    
    horizontal_offset = max(
        footprint_size * 0.30,
        100.0
    )

    vertical_offset = max(
        footprint_size * 2.20,
        600.0
    )
    
    camera_location = (
        focus_location
        + target.get_actor_right_vector()
        * horizontal_offset
        + unreal.Vector(
            0.0,
            0.0,
            vertical_offset
        )
    )

    camera_rotation = (
        unreal.MathLibrary.find_look_at_rotation(
            camera_location,
            focus_location
        )
    )
    
    # for mesh in validMeshes:
        # get_actor_bounds get the center of the mesh as first item, and the bounding box of the item as second
        # return type is a tuple
    #    MHBounds = mesh.get_actor_bounds(False)
    #    location = MHBounds[0] + mesh.get_actor_right_vector() * 500.0 + unreal.Vector(0.0, 0.0, MHBounds[1].z * 2)
        
    #    rotation = unreal.MathLibrary.find_look_at_rotation(
    #        location,
    #        MHBounds[0]
    #    )
        
    if cam is None:
        cam = ELL.spawn_actor_from_class(
            unreal.CineCameraActor,
            camera_location,
            camera_rotation
        )
        if cam is None:
            unreal.log_error(
                "CineCameraActor could not be spawned."
            )
            return None

        cam.tags.append(
            unreal.Name("dataset_camera")
        )

        cam.tags.append(camera_tag)

        cam.set_actor_label(
            f"CAM_{target.get_actor_label()}"
        )

        unreal.log(
            f"Created camera for "
            f"{target.get_actor_label()}"
        )

    cam.set_actor_location(
        camera_location,
        False,
        True
    )

    cam.set_actor_rotation(
        camera_rotation,
        True
    )

    unreal.log(
        f"Camera aimed at "
        f"{target.get_actor_label()}"
    )

    return cam

def setStart(mesh, channels, start_frame):
    # set the start frame as the same as the spawn loc and rot
    initial_location = mesh.get_actor_location()
    initial_rotation = mesh.get_actor_rotation()

    channels[0].add_key(
        start_frame,
        initial_location.x
    )

    channels[1].add_key(
        start_frame,
        initial_location.y
    )

    channels[2].add_key(
        start_frame,
        initial_location.z
    )
    
    channels[3].add_key(
        start_frame,
        initial_rotation.pitch
    )

    channels[4].add_key(
        start_frame,
        initial_rotation.roll
    )

    channels[5].add_key(
        start_frame,
        initial_rotation.yaw
    )


# create a level sequence

def createSequence(target, camera, sequence_name):
    if camera is None:
        unreal.log_error(
            "createSequence received no camera."
        )
        return None

    sequence_name = (
        sequence_name
        .replace(".", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )

    asset_path = (
        f"/Game/Sequences/{sequence_name}"
    )

    if EAL.does_asset_exist(asset_path):
        EAL.delete_asset(asset_path)

    asset_tools = (
        unreal.AssetToolsHelpers.get_asset_tools()
    )

    sequence = asset_tools.create_asset(
        sequence_name,
        "/Game/Sequences",
        unreal.LevelSequence,
        unreal.LevelSequenceFactoryNew()
    )

    if sequence is None:
        unreal.log_error(
            f"Could not create {sequence_name}."
        )
        return None

    sequence.set_display_rate(
        unreal.FrameRate(
            numerator=FPS,
            denominator=1
        )
    )

    sequence.set_playback_start(0)
    sequence.set_playback_end(TOTAL_FRAMES)

    camera_binding = sequence.add_possessable(
        camera
    )
    
    target_binding = sequence.add_possessable(
        target
    )

    camera_cut_track = sequence.add_track(
        unreal.MovieSceneCameraCutTrack
    )

    camera_cut_section = (
        camera_cut_track.add_section()
    )

    camera_cut_section.set_range(
        0,
        TOTAL_FRAMES
    )

    camera_binding_id = (
        unreal.MovieSceneObjectBindingID()
    )

    camera_binding_id.set_editor_property(
        "guid",
        camera_binding.get_id()
    )

    camera_cut_section.set_camera_binding_id(
        camera_binding_id
    )

    EAL.save_loaded_asset(sequence)

    unreal.log(
        f"Created {sequence_name}: "
        f"{VIDEO_SECONDS} seconds, "
        f"{TOTAL_FRAMES} frames."
    )

    return sequence.get_path_name()
    
def findSunSky():
    for actor in ELL.get_all_level_actors():
        actor_label = actor.get_actor_label()
        class_name = actor.get_class().get_name()

        if (
            actor_label == "SunSky"
            or "SunSky" in class_name
        ):
            return actor

    unreal.log_error(
        "SunSky Actor was not found."
    )

    return None

def setSunTime(hour, minute=0):

    sun_sky = findSunSky()

    if sun_sky is None:
        return False

    solar_time = (
        float(hour)
        + float(minute) / 60.0
    )

    try:
        sun_sky.set_editor_property(
            "SolarTime",
            solar_time
        )

        unreal.log(
            f"SolarTime set to {solar_time}"
        )

    except Exception as error:

        unreal.log_error(
            f"Could not set SolarTime: {error}"
        )

        return False


    except Exception as error:

        unreal.log_warning(
            f"Could not refresh SunSky: {error}"
        )


    actual_time = (
        sun_sky.get_editor_property(
            "SolarTime"
        )
    )

    unreal.log(
        f"SunSky changed: "
        f"{hour:02d}:{minute:02d}, "
        f"actual={actual_time}"
    )

    ELL.save_current_level()

    return True

def render(path, hour, minute, location_id):
    global _active_capture
    global _active_callback

    time_id = f"{hour:02d}{minute:02d}"

    capture = unreal.AutomatedLevelSequenceCapture()

    capture.level_sequence_asset = unreal.SoftObjectPath(
        path
    )

    capture.set_image_capture_protocol_type(
        unreal.ImageSequenceProtocol_PNG
    )

    settings = capture.settings

    settings.output_directory = unreal.DirectoryPath(
        f"{RENDER_ROOT}/"
        f"{location_id}/"
        f"{time_id}"
    )

    settings.output_format = (
        f"{location_id}_{time_id}_"
        "{frame}"
    )

    settings.overwrite_existing = True
    settings.use_relative_frame_numbers = True
    settings.zero_pad_frame_numbers = 4

    settings.use_custom_frame_rate = True
    settings.custom_frame_rate = unreal.FrameRate(
        numerator=FPS,
        denominator=1
    )

    settings.resolution = unreal.CaptureResolution(
        640,
        360
    )

    settings.cinematic_engine_scalability = False
    settings.enable_texture_streaming = True
    settings.cinematic_mode = False
    settings.show_hud = False
    settings.show_player = False

    callback = unreal.OnRenderMovieStopped()
    callback.bind_callable(
        onRenderFinished
    )

    _active_capture = capture
    _active_callback = callback

    protocol = capture.get_image_capture_protocol()

    unreal.log(
        f"Capture protocol: "
        f"{protocol.get_class().get_name()}"
    )
    unreal.log(
        f"Starting capture: "
        f"{time_id}, frames={TOTAL_FRAMES}"
    )

    started = unreal.SequencerTools.render_movie(
        capture,
        callback
    )

    unreal.log(
        f"render_movie returned: {started}"
    )

    if not started:
        unreal.log_error(
            f"Render could not start for {time_id}."
        )

        _active_capture = None
        _active_callback = None
        return False

    return True

def renderNext():
    global _render_index

    unreal.log(
        f"Render index = {_render_index}"
    )

    if _render_index >= len(RENDER_TIMES):
        unreal.log(
            "All solar-time videos "
            "have finished."
        )
        return

    hour, minute = RENDER_TIMES[
        _render_index
    ]

    if not setSunTime(hour, minute):
        unreal.log_error(
            f"Could not set sunlight for "
            f"{hour:02d}:{minute:02d}."
        )
        return

    render(
        _render_sequence_path,
        hour,
        minute,
        _render_location_id
    )
       
def start_render_jobs(
    target,
    camera,
    sequence_path
):
    global _render_index
    global _render_sequence_path
    global _render_location_id

    if target is None:
        unreal.log_error(
            "No target was supplied to render jobs."
        )
        return

    if camera is None:
        unreal.log_error(
            "No camera was supplied to render jobs."
        )
        return

    if sequence_path is None:
        unreal.log_error(
            "No Sequence was supplied."
        )
        return

    try:
        if unreal.SequencerTools.is_rendering_movie():
            unreal.log_error(
                "Another movie render is already running."
            )
            return
    except Exception:
        pass

    _render_index = 0
    _render_sequence_path = sequence_path

    _render_location_id = (
        target.get_actor_label()
        .replace(".", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )

    unreal.log(
        f"Starting render jobs for "
        f"{_render_location_id}."
    )

    renderNext()
    
def onRenderFinished(success):
    global _render_index
    global _active_capture
    global _active_callback

    hour, minute = RENDER_TIMES[
        _render_index
    ]

    unreal.log(
        f"Finished {hour:02d}:{minute:02d}; "
        f"success={success}"
    )

    _active_capture = None
    _active_callback = None

    if not success:
        unreal.log_error(
            "Render queue stopped because "
            "the current render failed."
        )
        return

    _render_index += 1

    renderNext()

def run_all(la, lo):
    target = spawn(la, lo)

    if target is None:
        unreal.log_error(
            "Target creation failed."
        )
        return

    camera = spawnCam(target)

    if camera is None:
        unreal.log_error(
            "Camera creation failed."
        )
        return

    location_id = make_location_id(
        la,
        lo
    )

    sequence_name = (
        f"SEQ_{location_id}"
    )

    sequence_path = createSequence(
        target,
        camera,
        sequence_name
    )

    if sequence_path is None:
        unreal.log_error(
            "Sequence creation failed."
        )
        return

    start_render_jobs(
        target,
        camera,
        sequence_path
    )