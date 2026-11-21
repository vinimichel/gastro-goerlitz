/* Google Analytics (via the Google tag GTM-PF78BVK6) loads only after the visitor
   agrees in the consent bar, as § 25 TDDDG requires. The choice is kept in
   localStorage under "ga-consent" ("granted" or "denied"). "Cookie-Einstellungen"
   in the footer reopens the bar, so consent can be withdrawn as easily as given. */
(() => {
  const KEY = "ga-consent";
  const TAG_ID = "GTM-PF78BVK6";

  const stored = () => { try { return localStorage.getItem(KEY); } catch { return null; } };
  const store = (value) => { try { localStorage.setItem(KEY, value); } catch {} };

  let loaded = false;
  function loadAnalytics() {
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    // Consent covers analytics only, so Google's advertising features stay off.
    gtag("consent", "default", {
      analytics_storage: "granted",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
    });
    gtag("js", new Date());
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtm.js?id=" + TAG_ID;
    document.head.appendChild(script);
  }

  // Removes _ga, _ga_<id>, _gid and _gat cookies on this host and its parent domain.
  function clearAnalyticsCookies() {
    const host = location.hostname;
    document.cookie.split(";").forEach((pair) => {
      const name = pair.split("=")[0].trim();
      if (!/^(_ga(_.+)?|_gid|_gat.*)$/.test(name)) return;
      ["", "; domain=" + host, "; domain=." + host].forEach((domain) => {
        document.cookie = name + "=; Max-Age=0; path=/" + domain;
      });
    });
  }

  let bar = null;
  function showBar() {
    if (!bar) {
      bar = document.createElement("section");
      bar.className = "consent";
      bar.setAttribute("aria-label", "Einwilligung in Google Analytics");
      bar.innerHTML =
        '<div class="wrap">' +
        "<p>Dürfen wir mit Google Analytics messen, wie oft diese Seite aufgerufen wird und welche Abschnitte gelesen werden? " +
        "Dafür setzt Google Cookies und erhält Nutzungsdaten, die auch in die USA übertragen werden können. " +
        'Ihre Wahl können Sie jederzeit unter „Cookie-Einstellungen“ am Seitenende ändern. Mehr dazu in der <a href="/datenschutz.html">Datenschutzerklärung</a>.</p>' +
        '<div class="consent-actions">' +
        '<button type="button" data-choice="denied">Ablehnen</button>' +
        '<button type="button" data-choice="granted">Akzeptieren</button>' +
        "</div></div>";
      bar.addEventListener("click", (e) => {
        const button = e.target.closest("button[data-choice]");
        if (button) choose(button.dataset.choice);
      });
      document.body.append(bar);
      // Keep the end of the page reachable while the bar covers it.
      new ResizeObserver(() => {
        document.body.style.paddingBottom = bar.hidden ? "" : bar.offsetHeight + "px";
      }).observe(bar);
    }
    bar.hidden = false;
    document.body.style.paddingBottom = bar.offsetHeight + "px";
  }

  function hideBar() {
    if (!bar) return;
    bar.hidden = true;
    document.body.style.paddingBottom = "";
  }

  function choose(choice) {
    const previous = stored();
    store(choice);
    hideBar();
    if (choice === "granted") {
      loadAnalytics();
    } else if (previous === "granted" || loaded) {
      // Withdrawn: delete the cookies and reload so the running tag stops.
      clearAnalyticsCookies();
      location.reload();
    }
  }

  document.querySelectorAll("[data-consent-open]").forEach((button) => {
    button.hidden = false;
    button.addEventListener("click", showBar);
  });

  const choice = stored();
  if (choice === "granted") loadAnalytics();
  else if (choice !== "denied") showBar();
})();
