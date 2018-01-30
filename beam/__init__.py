import flask
from .views import FromTextView

# pylint: disable=invalid-name
dataflow_bp = flask.Blueprint('dataflow', __name__)


dataflow_bp.add_url_rule(
    '/from_text',
    view_func=FromTextView.as_view('from_text')
)
