import pytest

from instinto.errors import SourceError
from instinto.world.loaders import MapLoader, ObjectLoader, TerrainLoader
from instinto.world.repository import Repository

GRASS = "# grass.te\nterrain Grass\nchar .\nresource_max 100\nregen 2\n"
ROCK = "# rock.ob\nobject Rock\nchar #\nresource_max 100\n"


def parse_terrain(text):
    return TerrainLoader().parse(text, "terrains/t.te")


def parse_object(text):
    return ObjectLoader().parse(text, "objects/o.ob")


def base_repo():
    repo = Repository()
    repo.register_element(parse_terrain(GRASS))
    repo.register_element(parse_object(ROCK))
    return repo


def parse_map(text, repo=None):
    return MapLoader(repo or base_repo()).parse(text, "maps/m.map")


def error_of(fn, *args):
    with pytest.raises(SourceError) as info:
        fn(*args)
    return info.value


# ---------------- .te / .ob ----------------

def test_teacher_grass():
    grass = parse_terrain(GRASS)
    assert (grass.name, grass.char, grass.resource_max, grass.regen) == ("Grass", ".", 100, 2)


def test_teacher_rock():
    rock = parse_object(ROCK)
    assert (rock.name, rock.char, rock.resource_max) == ("Rock", "#", 100)


def test_hash_as_char_is_a_value_not_a_comment():
    assert parse_object("object W\nchar #\nresource_max 5").char == "#"


def test_trailing_comment_after_value():
    grass = parse_terrain("terrain G\nchar . # dot\nresource_max 100 # big\nregen 2")
    assert grass.char == "." and grass.resource_max == 100


def test_any_key_order():
    t = parse_terrain("regen 1\nresource_max 9\nchar ~\nterrain Water")
    assert t.name == "Water" and t.regen == 1


def test_extra_keys_are_kept_for_extensions():
    t = parse_terrain(GRASS + "slows 2\n")
    assert t.extra == {"slows": "2"}


def test_regen_zero_allowed_resource_max_zero_not():
    assert parse_terrain("terrain L\nchar ^\nresource_max 1\nregen 0").regen == 0
    err = error_of(parse_terrain, "terrain L\nchar ^\nresource_max 0\nregen 0")
    assert err.line == 3 and "resource_max" in err.message


def test_missing_key_is_reported():
    err = error_of(parse_object, "object Rock\nchar #\n")
    assert "resource_max" in err.message and err.source == "objects/o.ob"


def test_terrain_without_regen_is_rejected():
    assert "regen" in error_of(parse_terrain, "terrain G\nchar .\nresource_max 1").message


def test_duplicate_key_points_at_second_line():
    err = error_of(parse_object, "object R\nchar #\nresource_max 1\nchar @\n")
    assert err.line == 4


def test_bad_integer_line_number():
    err = error_of(parse_terrain, "terrain G\nchar .\nresource_max lots\nregen 2")
    assert err.line == 3


def test_multichar_char():
    assert error_of(parse_object, "object R\nchar ##\nresource_max 1").line == 2


def test_key_without_value_and_junk_after_value():
    assert error_of(parse_object, "object R\nchar\nresource_max 1").line == 2
    assert error_of(parse_object, "object R extra\nchar #\nresource_max 1").line == 1


def test_empty_file():
    assert error_of(parse_object, "").line == 1


def test_crlf_line_endings():
    assert parse_object("object Rock\r\nchar #\r\nresource_max 100\r\n").name == "Rock"


# ---------------- maps ----------------

def test_map_cells_resolved():
    m = parse_map("Tiny\n.....\n.#...\n.....\n")
    assert (m.name, m.width, m.height) == ("Tiny", 5, 3)
    assert m.objects[1][1].name == "Rock"
    assert m.terrains[1][1].name == "Grass"      # rock sits on grass
    assert m.objects[0][0] is None


def test_map_crlf_and_trailing_blank_lines():
    m = parse_map("Tiny\r\n...\r\n.#.\r\n\r\n\r\n")
    assert (m.width, m.height) == (3, 2)


def test_unknown_char_reports_char_and_line():
    err = error_of(parse_map, "Tiny\n...\n.%.\n")
    assert err.line == 3 and "'%'" in err.message and err.source == "maps/m.map"


def test_ragged_row():
    assert error_of(parse_map, "Tiny\n....\n...\n").line == 3


def test_blank_row_in_the_middle_is_an_error():
    assert error_of(parse_map, "Tiny\n...\n\n...\n").line == 3


def test_map_without_rows_or_name():
    assert error_of(parse_map, "Only a name\n").line == 1
    assert error_of(parse_map, "").line == 1


def test_object_char_without_any_terrain():
    repo = Repository()
    repo.register_element(parse_object(ROCK))
    assert "terrain" in error_of(parse_map, "M\n#\n", repo).message


# ---------------- repository ----------------

def test_duplicate_char_rejected_with_line_of_char():
    repo = base_repo()
    other = parse_terrain("terrain Sand\nchar .\nresource_max 1\nregen 0")
    err = error_of(repo.register_element, other)
    assert err.line == 2 and "Grass" in err.message


def test_char_shared_between_terrain_and_object_rejected():
    repo = base_repo()
    err = error_of(repo.register_element, parse_object("object Wall\nchar .\nresource_max 1"))
    assert "already used" in err.message


def test_duplicate_name_rejected():
    repo = base_repo()
    err = error_of(repo.register_element, parse_object("object Grass\nchar G\nresource_max 1"))
    assert err.line == 1


def test_default_terrain_is_grass_even_if_another_is_loaded_first():
    repo = Repository()
    repo.register_element(parse_terrain("terrain Dirt\nchar ,\nresource_max 1\nregen 0"))
    repo.register_element(parse_terrain(GRASS))
    assert repo.default_terrain.name == "Grass"


def write(root, folder, name, text):
    (root / folder).mkdir(exist_ok=True)
    (root / folder / name).write_text(text, encoding="utf-8")


def test_load_all_teacher_data():
    repo = Repository().load_all(".")
    assert repo.errors == []
    assert [t.name for t in repo.terrains] == ["Grass"]
    assert [o.name for o in repo.objects] == ["Rock"]
    m = repo.maps[0]
    assert m.name == "Plain with rocks" and (m.width, m.height) == (20, 7)


def test_bad_files_are_reported_and_loading_continues(tmp_path):
    write(tmp_path, "terrains", "grass.te", GRASS)
    write(tmp_path, "terrains", "broken.te", "terrain B\nchar b\n")
    write(tmp_path, "terrains", "ignored.txt", "not a terrain")
    write(tmp_path, "objects", "rock.ob", ROCK)
    write(tmp_path, "maps", "good.map", "Good\n.#.\n")
    write(tmp_path, "maps", "bad.map", "Bad\n.?.\n")
    (tmp_path / "terrains" / "binary.te").write_bytes(b"\xff\xfe\x00\x80")

    repo = Repository().load_all(tmp_path)

    assert [t.name for t in repo.terrains] == ["Grass"]
    assert [m.name for m in repo.maps] == ["Good"]
    messages = sorted(str(e) for e in repo.errors)
    assert len(messages) == 3
    assert any("broken.te" in m and "resource_max" not in m or "missing" in m for m in messages)
    assert any("bad.map:2" in m and "'?'" in m for m in messages)
    assert any("binary.te" in m and "UTF-8" in m for m in messages)


def test_missing_directory_is_an_error_not_a_crash(tmp_path):
    repo = Repository().load_all(tmp_path)
    assert len(repo.errors) == 3 and repo.terrains == []
