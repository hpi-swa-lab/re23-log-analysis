from dash import Dash, html, dcc, callback, Output, Input, State
from ErrorAnalyzer import ErrorAnalyzer
from FailureDataCollector import FailureDataCollectorConstant
from DataFrameAdapter import DataFrameAdapter
import plotly.express as px

app = Dash(__name__)

# Analyzer for the data from the graalpy test run
root_analyzer = ErrorAnalyzer(
    FailureDataCollectorConstant(
        "graalpy-test-results.xml", "cpython-test-results.xml", "results/", "results/"
    )
)

# Group of filter inputs to filter the error documents
filter_group = (
    html.Div(
        [
            html.Div(
                [
                    html.Label("Filter {}:".format(_)),
                    dcc.Input(
                        id="input-{}".format(_),
                        type="text",
                        placeholder="filter {}".format(_),
                        style={"margin-left": "10px"},
                    ),
                ]
            )
            for _ in ["message", "type", "package", "stacktrace"]
        ],
        style={
            "display": "flex",
            "flex-direction": "row",
            "gap": "10px",
            "padding": "10px",
        },
    ),
)

# Histograms to display the distribution of the error messages
error_message_histogram = dcc.Loading(
    [dcc.Graph(figure={}, id="plot-hist-message")],
    type="default",
)
# Histograms to display the distribution of the error types
error_type_histogram = dcc.Loading(
    [dcc.Graph(figure={}, id="plot-hist-type")],
    type="default",
)

# Histograms to display the distribution of the packages
package_histogram = dcc.Loading(
    [dcc.Graph(figure={}, id="plot-hist-package")],
    type="default",
)

# Histograms to display the distribution of the last stacktrace lines
stacktrace_histogram = dcc.Loading(
    [dcc.Graph(figure={}, id="plot-hist-stacktrace")],
    type="default",
)

# Group of histograms
histogram_group = (
    html.Table(
        [
            html.Tr(
                [
                    html.Td(
                        [error_message_histogram],
                        style={"width": "50%"},
                    ),
                    html.Td([error_type_histogram]),
                ]
            ),
            html.Tr(
                [
                    html.Td(
                        [package_histogram],
                        style={"width": "50%"},
                    ),
                    html.Td([stacktrace_histogram]),
                ]
            ),
        ],
        style={"width": "100%"},
    ),
)

# Display filtered error documents including the package, message, type and complete stacktrace
error_group = dcc.Loading(
    [
        html.Div(
            id="all-documents",
            style={
                "display": "flex",
                "flex-direction": "column",
                "gap": "10px",
                "padding": "10px",
            },
        ),
        html.Button("Load more", id="load-more-button", type="submit"),
        dcc.Store(id="loaded-documents", data=0),
    ]
)


# Builds a component to display a single error document
def build_error_component(error):
    subtitle = (
        "{}: {}".format(error.errorType, error.errorMessage)
        if error.errorType
        else error.errorMessage
    )
    return html.Div(
        [
            html.H3(
                [error.packageName],
            ),
            html.I([subtitle]),
            html.Br(),
            html.Br(),
            html.Div(
                [
                    html.Code([line, html.Br()], style={"paddingBottom": "2px"})
                    for line in error.stackTrace.split("\n")
                ]
            ),
        ],
        style={
            "padding": "10px",
            "border": "1px solid black",
            "border-radius": "5px",
        },
    )


app.layout = html.Div(
    [
        html.Div(
            [error_group],
            style={"width": "30%", "height": "100vh", "overflow": "scroll"},
        ),
        html.Div(
            [html.H1(["Graalpy Log Analysis"]), *filter_group, *histogram_group],
            style={"width": "70%"},
        ),
    ],
    style={"display": "flex", "flex-direction": "row", "gap": "10px"},
)


@callback(
    Output(component_id="plot-hist-message", component_property="figure"),
    Output(component_id="plot-hist-type", component_property="figure"),
    Output(component_id="plot-hist-package", component_property="figure"),
    Output(component_id="plot-hist-stacktrace", component_property="figure"),
    Output(component_id="all-documents", component_property="children"),
    Output(component_id="plot-hist-message", component_property="clickData"),
    Output(component_id="plot-hist-type", component_property="clickData"),
    Output(component_id="plot-hist-package", component_property="clickData"),
    Output(component_id="plot-hist-stacktrace", component_property="clickData"),
    Output(component_id="input-message", component_property="value"),
    Output(component_id="input-type", component_property="value"),
    Output(component_id="input-package", component_property="value"),
    Output(component_id="input-stacktrace", component_property="value"),
    Input(component_id="input-message", component_property="value"),
    Input(component_id="input-type", component_property="value"),
    Input(component_id="input-package", component_property="value"),
    Input(component_id="input-stacktrace", component_property="value"),
    Input(component_id="loaded-documents", component_property="data"),
    Input(component_id="plot-hist-message", component_property="clickData"),
    Input(component_id="plot-hist-type", component_property="clickData"),
    Input(component_id="plot-hist-package", component_property="clickData"),
    Input(component_id="plot-hist-stacktrace", component_property="clickData"),
)
def filter_package(
    filter_message,
    filter_type,
    filter_package,
    filter_stacktrace,
    loaded_documents,
    click_data_message,
    click_data_type,
    click_data_package,
    click_data_stacktrace,
):
    analyzer = root_analyzer
    # Check if the user clicked on a histogram bar to filter the error documents
    filter_message = extract_x_from_click_data(click_data_message) or filter_message
    filter_type = extract_x_from_click_data(click_data_type) or filter_type
    filter_package = extract_x_from_click_data(click_data_package) or filter_package
    filter_stacktrace = (
        extract_x_from_click_data(click_data_stacktrace) or filter_stacktrace
    )

    # Filter the error documents if the user entered a filter
    if filter_package is not None:
        analyzer = analyzer.filter_packages(filter_package)
    if filter_message is not None:
        analyzer = analyzer.filter_error_message(filter_message)
    if filter_type is not None:
        analyzer = analyzer.filter_error_type(filter_type)
    if filter_stacktrace is not None:
        analyzer = analyzer.filter_stacktrace(filter_stacktrace)

    # Adapter from internal error documents to pandas data frame
    dict_adapter = DataFrameAdapter(analyzer)

    package_df = dict_adapter.get_packages_df()
    type_df = dict_adapter.get_error_types_df()
    message_df = dict_adapter.get_error_messages_df()
    stacktrace_df = dict_adapter.get_last_stacktrace_lines_df()

    # Build histograms from the data frames
    package = px.bar(package_df, x="package", y="count")
    types = px.bar(type_df, x="error type", y="count")
    message = px.bar(message_df, x="error message", y="count")
    stacktrace = px.bar(stacktrace_df, x="last stacktrace line", y="count")

    # Build list of error components to display them in left column
    all_error_documents = analyzer.error_documents
    all_error_documents.sort(key=lambda _: _.packageName.lower())
    error_components = [
        build_error_component(error) for error in all_error_documents[:loaded_documents]
    ]

    # Reset the click data to allow the user to click for filtering again
    empty_click_data = {"points": []}
    return (
        message,
        types,
        package,
        stacktrace,
        error_components,
        empty_click_data,
        empty_click_data,
        empty_click_data,
        empty_click_data,
        filter_message,
        filter_type,
        filter_package,
        filter_stacktrace,
    )


@callback(
    Output(component_id="loaded-documents", component_property="data"),
    Input(component_id="load-more-button", component_property="n_clicks"),
    Input(component_id="loaded-documents", component_property="data"),
)
def increase_loaded_documents(n_clicks, loaded_documents):
    """
    Increases the number of loaded documents by 10 if the user clicks on the "load more" button.
    Paginates the error documents.
    """
    return loaded_documents + 10


def extract_x_from_click_data(click_data):
    """
    Extracts the x value from a click data object, e.g., a bar in a histogram.
    """
    if (
        click_data is not None
        and click_data["points"] is not None
        and len(click_data["points"]) > 0
    ):
        return click_data["points"][0]["x"]
    return None


if __name__ == "__main__":
    app.run(debug=True)
