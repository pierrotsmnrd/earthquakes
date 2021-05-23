import panel as pn
from earthquakes_app import EarthquakesApp
import gettext


def earthquakes_page(**kwargs):

    print("earthquakes page", flush=True)

    lang_id = None
    if 'lg' in pn.state.session_args.keys():
        try:
            lang_id = pn.state.session_args.get('lg')[0].decode('utf-8')
        except:
            pass

    print("lang id CAC", lang_id)

    component = EarthquakesApp(lang_id=lang_id)
    return component.view()


if __name__ == "__main__":

    server = pn.serve({'/earthquakes': earthquakes_page, },
                      title={'/earthquakes': 'Earthquakes'},
                      websocket_origin=["*"],
                      autoreload=True,
                      port=80,
                      )
