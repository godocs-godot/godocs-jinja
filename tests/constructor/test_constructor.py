from pathlib import Path
import jinja2 as j2
from textwrap import dedent

from godocs_jinja.constructor import JinjaConstructor

TEST_FILTERS = """
def filter1(): return ""
def filter2(): return ""
def filter3(): return ""
"""

TEST_BUILDERS = """
def builder1(f, t, c, p): pass
def builder2(f, t, c, p): pass
def builder3(f, t, c, p): pass
"""

# TEST_BUILDERS: dict[str, Builder] = {
#     "builder1": lambda f, t, c, p: None,
#     "builder2": lambda f, t, c, p: None,
#     "builder3": lambda f, t, c, p: None,
# }


def test_build_template_writes_to_file(tmp_path: Path):
    # Arrange
    env = j2.Environment(loader=j2.DictLoader(
        {"test_template": "Hello, {{ name }}!"}))

    template = env.get_template("test_template")

    # Act
    JinjaConstructor.build_template(
        name="output",
        format="rst",
        template=template,
        context={"name": "Test"},
        path=tmp_path,
    )

    # Assert
    result = tmp_path.joinpath("output.rst").read_text()

    assert result == "Hello, Test!"


def test_build_class_templates_writes_to_files(tmp_path: Path):
    # Arrange
    env = j2.Environment(loader=j2.DictLoader(
        {"class": "{{class.name}}"}))

    template = env.get_template("class")

    # Act
    JinjaConstructor.build_class_templates(
        template=template,
        format="rst",
        context={"classes": [
            {"name": "Class1"},
            {"name": "Class2"},
            {"name": "Class3"},
        ]},
        path=tmp_path,
    )

    # Assert
    class1_doc = tmp_path.joinpath("class1.rst").read_text()
    class2_doc = tmp_path.joinpath("class2.rst").read_text()
    class3_doc = tmp_path.joinpath("class3.rst").read_text()

    assert class1_doc == "Class1"
    assert class2_doc == "Class2"
    assert class3_doc == "Class3"


def test_build_index_template_writes_to_file(tmp_path: Path):
    # Arrange
    template_content = dedent("""
        {% for class in classes -%}
        {{class.name}}
        {% endfor %}
    """.strip("\n"))

    env = j2.Environment(loader=j2.DictLoader(
        {"index": template_content}))

    template = env.get_template("index")

    # Act
    JinjaConstructor.build_index_template(
        template=template,
        format="rst",
        context={"classes": [
            {"name": "Class1"},
            {"name": "Class2"},
            {"name": "Class3"},
        ]},
        path=tmp_path,
    )

    # Assert
    index_doc = tmp_path.joinpath("index.rst").read_text()

    index_content = dedent("""
        Class1
        Class2
        Class3
    """.strip("\n"))

    assert index_doc == index_content


def test_default_construction():
    # Act
    constructor = JinjaConstructor()

    # Assert
    assert len(constructor.builders) == 2
    assert "class" in constructor.builders
    assert "index" in constructor.builders
    assert len(constructor.filters) == 7
    assert constructor.model is not None
    assert constructor.model.stem == "rst"
    assert len(constructor.models) == 1
    assert constructor.models[0].stem == "rst"
    assert len(constructor.templates) == 2
    assert constructor.templates[0].stem == "class"
    assert constructor.templates[1].stem == "index"
    assert constructor.templates_path is not None
    assert constructor.templates_path.stem == "templates"
    assert constructor.templates_path.parent.stem == "rst"


def test_default_construction_with_model(tmp_path: Path):
    # Arrange
    model = tmp_path / "model"

    # Act
    constructor = JinjaConstructor(model=model)

    # Assert
    assert len(constructor.builders) == 2
    assert "class" in constructor.builders
    assert "index" in constructor.builders
    assert len(constructor.models) == 1
    assert constructor.models[0].stem == "rst"
    assert constructor.model is not None
    assert constructor.model.stem == "model"
    assert len(constructor.templates) == 0
    assert len(constructor.filters) == 0
    assert constructor.templates_path is not None
    assert constructor.templates_path.stem == "templates"
    assert constructor.templates_path.parent.stem == "model"


def test_default_construction_with_model_with_templates(tmp_path: Path):
    # Arrange
    model = tmp_path / "model"
    templates = model / "templates"
    template1 = templates / "template1.jinja"
    template2_dir = templates / "template2"
    template2 = template2_dir / "index.jinja"

    templates.mkdir(parents=True, exist_ok=True)
    template1.touch()
    template2_dir.mkdir()
    template2.touch()

    # Act
    constructor = JinjaConstructor(model=model)

    # Assert
    assert len(constructor.models) == 1
    assert constructor.models[0].stem == "rst"
    assert constructor.model is not None
    assert constructor.model.stem == "model"
    assert constructor.templates_path is not None
    assert constructor.templates_path.stem == "templates"
    assert constructor.templates_path.parent.stem == "model"
    assert len(constructor.templates) == 2
    assert constructor.templates[0].stem == "template1"
    assert constructor.templates[1].stem == "template2"
    assert len(constructor.filters) == 0
    assert len(constructor.builders) == 2
    assert "class" in constructor.builders
    assert "index" in constructor.builders


def test_default_construction_with_model_with_filters(tmp_path: Path):
    # Arrange
    model = tmp_path / "model"
    filters_script = model / "filters.py"

    model.mkdir()
    filters_script.write_text(TEST_FILTERS)

    # Act
    constructor = JinjaConstructor(model=model)

    # Assert
    assert len(constructor.models) == 1
    assert constructor.models[0].stem == "rst"
    assert constructor.model is not None
    assert constructor.model.stem == "model"
    assert constructor.templates_path is not None
    assert constructor.templates_path.stem == "templates"
    assert constructor.templates_path.parent.stem == "model"
    assert len(constructor.templates) == 0
    assert len(constructor.filters) == 3
    assert constructor.filters[0][0] == "filter1"
    assert constructor.filters[1][0] == "filter2"
    assert constructor.filters[2][0] == "filter3"
    assert len(constructor.builders) == 2
    assert "class" in constructor.builders
    assert "index" in constructor.builders


def test_default_construction_with_templates_path(tmp_path: Path):
    # Arrange
    templates_path = tmp_path / "custom_templates"
    template1 = templates_path / "template1.jinja"
    template2_dir = templates_path / "template2"
    template2 = template2_dir / "index.jinja"

    templates_path.mkdir(parents=True, exist_ok=True)
    template1.touch()
    template2_dir.mkdir()
    template2.touch()

    # Act
    constructor = JinjaConstructor(templates_path=templates_path)

    # Assert
    assert len(constructor.models) == 1
    assert constructor.models[0].stem == "rst"
    assert constructor.model is not None
    assert constructor.model.stem == "rst"
    assert constructor.templates_path is not None
    assert constructor.templates_path.stem == "custom_templates"
    assert len(constructor.templates) == 2
    assert constructor.templates[0].stem == "template1"
    assert constructor.templates[1].stem == "template2"
    assert len(constructor.filters) == 7
    assert len(constructor.builders) == 2
    assert "class" in constructor.builders
    assert "index" in constructor.builders


def test_default_construction_with_filters_path(tmp_path: Path):
    # Arrange
    filters_path = tmp_path / "custom_filters.py"

    filters_path.write_text(TEST_FILTERS)

    # Act
    constructor = JinjaConstructor(filters_path=filters_path)

    # Assert
    assert len(constructor.models) == 1
    assert constructor.models[0].stem == "rst"
    assert constructor.model is not None
    assert constructor.model.stem == "rst"
    assert constructor.templates_path is not None
    assert constructor.templates_path.stem == "templates"
    assert len(constructor.templates) == 2
    assert constructor.templates[0].stem == "class"
    assert constructor.templates[1].stem == "index"
    assert len(constructor.filters) == 3
    assert constructor.filters[0][0] == "filter1"
    assert constructor.filters[1][0] == "filter2"
    assert constructor.filters[2][0] == "filter3"
    assert len(constructor.builders) == 2
    assert "class" in constructor.builders
    assert "index" in constructor.builders


def test_default_construction_with_builders_path(tmp_path: Path):
    # Arrange
    builders_path = tmp_path / "custom_builders.py"

    builders_path.write_text(TEST_BUILDERS)

    # Act
    constructor = JinjaConstructor(builders_path=builders_path)

    # Assert
    assert len(constructor.models) == 1
    assert constructor.models[0].stem == "rst"
    assert constructor.model is not None
    assert constructor.model.stem == "rst"
    assert constructor.templates_path is not None
    assert constructor.templates_path.stem == "templates"
    assert len(constructor.templates) == 2
    assert constructor.templates[0].stem == "class"
    assert constructor.templates[1].stem == "index"
    assert len(constructor.filters) == 7
    assert len(constructor.builders) == 3
    assert "builder1" in constructor.builders
    assert "builder2" in constructor.builders
    assert "builder3" in constructor.builders


def test_find_models_ignores_files(tmp_path: Path):
    # Arrange
    model1 = tmp_path / "model1"
    model2 = tmp_path / "model2"
    model3 = tmp_path / "model3.py"

    model1.mkdir()
    model2.mkdir()
    model3.touch()

    constructor = JinjaConstructor()

    # Act
    models = constructor.find_models(tmp_path)

    # Assert
    assert len(models) == 2
    assert models[0].stem == "model1"
    assert models[1].stem == "model2"


def test_find_models_ignores_pycache(tmp_path: Path):
    # Arrange
    model1 = tmp_path / "model1"
    model2 = tmp_path / "model2"
    model3 = tmp_path / "__pycache__"

    model1.mkdir()
    model2.mkdir()
    model3.mkdir()

    constructor = JinjaConstructor()

    # Act
    models = constructor.find_models(tmp_path)

    # Assert
    assert len(models) == 2
    assert models[0].stem == "model1"
    assert models[1].stem == "model2"


def test_find_model_returns_model_by_name():
    # Arrange
    constructor = JinjaConstructor()

    # Act
    model = constructor.find_model("rst")

    # Assert
    assert model is not None
    assert model.stem == "rst"
    assert model.parent.stem == "models"


def test_find_model_returns_not_found():
    # Arrange
    constructor = JinjaConstructor()

    # Act
    model = constructor.find_model("md")

    # Assert
    assert model is None


def test_find_templates_considers_files_and_folders(tmp_path: Path):
    # Arrange
    templates_path = tmp_path / "templates"
    template1_dir = templates_path / "template1"
    template2_dir = templates_path / "template2"
    template1 = template1_dir / "index.jinja"
    template2 = template2_dir / "index.jinja"
    template3 = templates_path / "template3.jinja"

    templates_path.mkdir()
    template1_dir.mkdir()
    template2_dir.mkdir()
    template1.touch()
    template2.touch()
    template3.touch()

    constructor = JinjaConstructor()

    # Act
    templates = constructor.find_templates(templates_path)

    # Assert
    assert len(templates) == 3
    assert templates[0].stem == "template1"
    assert templates[1].stem == "template2"
    assert templates[2].stem == "template3"


def test_find_templates_ignores_folders_without_index(tmp_path: Path):
    # Arrange
    templates_path = tmp_path / "templates"
    template1_dir = templates_path / "template1"
    template2_dir = templates_path / "template2"
    template1 = template1_dir / "index.jinja"
    template3 = templates_path / "template3.jinja"

    templates_path.mkdir()
    template1_dir.mkdir()
    template2_dir.mkdir()
    template1.touch()
    template3.touch()

    constructor = JinjaConstructor()

    # Act
    templates = constructor.find_templates(templates_path)

    # Assert
    assert len(templates) == 2
    assert templates[0].stem == "template1"
    assert templates[1].stem == "template3"


def test_find_templates_ignores_pycache(tmp_path: Path):
    # Arrange
    templates_path = tmp_path / "templates"
    template1_dir = templates_path / "template1"
    template2_dir = templates_path / "__pycache__"
    template1 = template1_dir / "index.jinja"
    template3 = templates_path / "template3.jinja"

    templates_path.mkdir()
    template1_dir.mkdir()
    template2_dir.mkdir()
    template1.touch()
    template3.touch()

    constructor = JinjaConstructor()

    # Act
    templates = constructor.find_templates(templates_path)

    # Assert
    assert len(templates) == 2
    assert templates[0].stem == "template1"
    assert templates[1].stem == "template3"


def test_find_templates_ignores_nonjinja_files(tmp_path: Path):
    # Arrange
    templates_path = tmp_path / "templates"
    template1_dir = templates_path / "template1"
    template1 = template1_dir / "index.jinja"
    template2 = templates_path / "template2.njk"
    template3 = templates_path / "template3.jinja"

    templates_path.mkdir()
    template1_dir.mkdir()
    template1.touch()
    template2.touch()
    template3.touch()

    constructor = JinjaConstructor()

    # Act
    templates = constructor.find_templates(templates_path)

    # Assert
    assert len(templates) == 2
    assert templates[0].stem == "template1"
    assert templates[1].stem == "template3"


def test_load_filters_extracts_functions_from_module(tmp_path: Path):
    # Arrange
    filters_script = tmp_path / "filters.py"

    # filters_script.touch()
    filters_script.write_text(TEST_FILTERS)

    constructor = JinjaConstructor()

    # Act
    filters = constructor.load_filters(filters_script)

    # Assert
    assert len(filters) == 3
    assert filters[0][0] == "filter1"
    assert filters[1][0] == "filter2"
    assert filters[2][0] == "filter3"


def test_register_filters_succeds():
    # Arrange
    filters = [
        ("filter1", lambda: ""),
        ("filter2", lambda: ""),
        ("filter3", lambda: ""),
    ]

    constructor = JinjaConstructor()

    env = j2.Environment()

    # Act
    env = constructor.register_filters(env, filters)

    # Assert
    assert "filter1" in env.filters  # type: ignore
    assert "filter2" in env.filters  # type: ignore
    assert "filter3" in env.filters  # type: ignore


def test_get_template_name_returns_relative_template_path(tmp_path: Path):
    # Arrange
    templates_path = tmp_path / "custom_templates"

    constructor = JinjaConstructor(templates_path=templates_path)

    assert constructor.templates_path is not None

    # Act
    result = constructor.get_template_name(
        constructor.templates_path / "custom_template")

    # Assert
    assert result == "custom_template"


def test_build_templates_uses_templates_and_builders(tmp_path: Path):
    # Arrange
    templates_path = tmp_path / "templates"
    template1_dir = templates_path / "template1"
    template1 = template1_dir / "index.jinja"
    template2 = templates_path / "template2.jinja"
    builders_path = tmp_path / "builders.py"
    builders_path.write_text("""
from godocs_jinja.constructor import JinjaConstructor

def template1(f, t, c, p): JinjaConstructor.build_template("doc1", f, t, c, p)
def template2(f, t, c, p): JinjaConstructor.build_template("doc2", f, t, c, p)
""")
    build_path = tmp_path / "build"

    templates_path.mkdir()
    template1_dir.mkdir()
    template1.write_text("Template1")
    template2.write_text("Template2")

    constructor = JinjaConstructor(
        templates_path=templates_path, builders_path=builders_path)

    assert constructor.env is not None

    # Act
    constructor.build_templates(constructor.env, context={}, path=build_path)

    # Assert
    doc1 = build_path.joinpath("doc1.rst").read_text()
    doc2 = build_path.joinpath("doc2.rst").read_text()

    assert doc1 == "Template1"
    assert doc2 == "Template2"
