import panel as pn
from earthquakes_app import EarthquakesApp, get_earthquakes_df


earthquakes_df = None


def earthquakes_page(**kwargs):

    print("earthquakes page", flush=True)

    lang_id = None
    if 'lg' in pn.state.session_args.keys():
        try:
            lang_id = pn.state.session_args.get('lg')[0].decode('utf-8')
        except:
            pass

    component = EarthquakesApp(lang_id=lang_id, df=earthquakes_df)
    return component.view()


if __name__ == "__main__":

    earthquakes_df = get_earthquakes_df()

    server = pn.serve({'/earthquakes': earthquakes_page, },
                      title={'/earthquakes': 'Earthquakes'},
                      websocket_origin=["*"],
                      autoreload=True,
                      port=80,
                      threaded=True,
                      # check_unused_sessions=3,
                      # unused_session_lifetime=3
                      )
