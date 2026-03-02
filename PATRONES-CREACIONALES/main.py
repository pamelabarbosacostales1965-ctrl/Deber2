config = AppConfig()
config.set_env('prod')
config.set_provider('gcp')

mensaje_base =(
    MessageBuilder()
    .to('user_01')
    .subject('sign_up')
)

mensaje_base.body('welcome to our service')

mensaje_base.prority(1).add_tag('onboarding').build()

