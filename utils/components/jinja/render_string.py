
from kfp import dsl


@dsl.component(
    packages_to_install=["Jinja2==3.1.2"]
)
def render_string_op(
        input_string: str,
        project: str = "",
        location: str = "us-central1",
        jinja_variables: dict = {},
        execution_timestamp: str = "",
) -> str:
    import jinja2

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
    rendered_string = render_string(
        input_string,
        **jinja_variables
    )
    return rendered_string

