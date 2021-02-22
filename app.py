from api import create_app
import api.config


app = create_app(api.config.DevelopmentConf)
# if __name__ == "__main__":
#     app.run()
