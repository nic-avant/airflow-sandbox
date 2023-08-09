from dags.hcio import hcio_task_alert_callback_base  # noqa: E402

URL = "https://hc-ping.com"
PROJECT_PING_KEY = '844d7hQguj_-hZ26ByMAeA'
SLUG = "data-80123"
# SLUG = "data-80124"


def test_hcio_task_alert_callback_base_success():
    r = hcio_task_alert_callback_base({}, slug=SLUG, success=True)
    return r

def test_hcio_task_alert_callback_base_fail():
    r = hcio_task_alert_callback_base({}, slug=SLUG, success=False)
    return r

if __name__ == "__main__":
    r = test_hcio_task_alert_callback_base_success()
    f = test_hcio_task_alert_callback_base_fail()
