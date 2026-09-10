import { createStaticURL } from '@splunk/splunk-utils/url';

// These were previously injected by the app's own Mako template,
// appserver/templates/start.html. That template was removed because AppInspect
// flags any custom Mako template under appserver/templates/
// (check_for_custom_mako_templates), and the platform template that replaced
// it, pages/splunk_ui_app.html, only bootstraps Splunk's own config, i18n and
// layout assets. App-owned CSS therefore has to be attached from the page
// bundle instead.
const stylesheets = ['app/censys/bootstrap-enterprise.css', 'app/censys/styles.css'];

export default function injectAppStyles() {
    stylesheets.forEach((path) => {
        const href = createStaticURL(path);
        if (document.head.querySelector(`link[rel="stylesheet"][href="${href}"]`)) {
            return;
        }
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = href;
        document.head.appendChild(link);
    });
}
