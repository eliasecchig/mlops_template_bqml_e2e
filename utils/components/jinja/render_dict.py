
from kfp import dsl


@dsl.component(
    packages_to_install=["Jinja2==3.1.2"]
)
def render_dict_op(
        input_dict: dict,
        project: str = "",
        location: str = "us-central1",
        jinja_variables: dict = {},
        execution_timestamp: str = "",
) -> dict:
    import jinja2
    import json

    from datetime import datetime

    def render_string(string, **kwargs):
        GLOBALS_JINJA = {"now": datetime.utcnow}
        rtemplate = jinja2.Environment(loader=jinja2.BaseLoader).from_string(string)
        data = rtemplate.render(**kwargs, **GLOBALS_JINJA)
        return data

    jinja_variables = {
        "project": project,
        "location": location,
        "execution_timestamp": execution_timestamp,
        **jinja_variables
    }
    rendered_dict = json.loads(render_string(
        json.dumps(input_dict),
        **jinja_variables
    ))
    return rendered_dict

