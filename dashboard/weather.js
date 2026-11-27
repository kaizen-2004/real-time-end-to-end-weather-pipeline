const byId = (id) => document.getElementById(id);
const freshFor = 90 * 60 * 1000;
const pht = new Intl.DateTimeFormat('en-PH', {
    dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Manila'
});

function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
}

function timestamp(value) {
    return typeof value === 'string' ? Date.parse(value) : NaN;
}

function hasReading(city) {
    return [city.temp, city.feels_like, city.humidity, city.wind].every(Number.isFinite)
        && city.humidity >= 0 && city.humidity <= 100 && city.wind >= 0;
}

function status(state, label, detail) {
    byId('snapshot-state').dataset.state = state;
    byId('snapshot-state').textContent = label;
    byId('snapshot-detail').textContent = detail;
}

function showSnapshot({ published_at }, cities, readings) {
    const count = readings.length;
    const temps = readings.map(({ temp }) => temp);
    const mean = (key) => readings.reduce((total, city) => total + city[key], 0) / count;
    byId('coverage').textContent = `${count} / ${cities.length}`;
    if (count) {
        byId('average-temp').textContent = `${mean('temp').toFixed(1)}°C`;
        byId('temp-range').textContent = `${Math.min(...temps)}–${Math.max(...temps)}°C`;
        byId('average-humidity').textContent = `${Math.round(mean('humidity'))}%`;
    }

    const published = timestamp(published_at);
    if (!count) {
        status('error', 'No readings available', 'None of the tracked cities has a reading in this snapshot.');
        return;
    }
    if (!Number.isFinite(published)) {
        status('stale', 'Archived snapshot', 'The original publication time is unknown. These readings may no longer reflect current conditions.');
        return;
    }
    const now = Date.now();
    const times = [published, ...readings.map(({ observed_at }) => timestamp(observed_at))];
    const isFresh = times.every((time) => time >= now - freshFor && time <= now + 5 * 60 * 1000);
    const detail = `Published ${pht.format(published)} PHT · ${count} of ${cities.length} cities reporting.`;
    if (!isFresh) {
        status('stale', 'Older or unverified readings', detail);
    } else if (count < cities.length) {
        status('partial', 'Partial snapshot', detail);
    } else {
        status('fresh', 'Recent snapshot', detail);
    }
}

function showDetail(city) {
    const available = hasReading(city);
    const data = [
        ['Feels like', available ? `${city.feels_like}°C` : '—'],
        ['Humidity', available ? `${city.humidity}%` : '—'],
        ['Wind', available ? `${city.wind} km/h` : '—']
    ];
    byId('detail-city').textContent = city.city;
    byId('detail-metrics').replaceChildren(...data.map(([label, value]) => {
        const item = element('div');
        item.append(element('dt', label), element('dd', value));
        return item;
    }));
    const observed = timestamp(city.observed_at);
    byId('detail-time').textContent = Number.isFinite(observed) && available
        ? `Observed ${pht.format(observed)} PHT`
        : available ? 'Observation time unavailable' : 'No observation in this snapshot';
    byId('city-detail').hidden = false;
}

function showBars(id, readings, key, unit, low, high) {
    const label = (value) => `${value}${unit}`;
    const percentage = (value) => (value - low) / (high - low) * 100;
    const rows = [...readings].sort((a, b) => b[key] - a[key]).map((city) => {
        const row = element('li');
        const track = element('span', undefined, 'bar-track');
        const fill = element('span', undefined, 'bar-fill');
        track.setAttribute('aria-hidden', 'true');
        fill.style.left = `${percentage(Math.min(0, city[key]))}%`;
        fill.style.width = `${Math.abs(percentage(city[key]) - percentage(0))}%`;
        track.append(fill);
        row.append(element('span', city.city), track, element('strong', label(city[key])));
        return row;
    });
    byId(id).replaceChildren(...(rows.length ? rows : [element('li', 'No readings available')]));
}

function initMap(cities, selectCity) {
    const message = byId('map-status');
    const surface = byId('map');
    const leaflet = window.L;
    if (!leaflet || getComputedStyle(surface).overflow !== 'hidden') {
        message.textContent = 'The map could not load. You can still explore the city readings.';
        return null;
    }

    surface.hidden = false;
    const map = leaflet.map(surface, { scrollWheelZoom: false, zoomSnap: 0.25, zoomDelta: 0.5 });
    const bounds = leaflet.latLngBounds(cities.map(({ lat, lon }) => [lat, lon]));
    const reset = () => map.closePopup().fitBounds(bounds, { padding: [30, 28], maxZoom: 9, animate: false });
    reset();
    const tiles = leaflet.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    });
    let hasTiles = false;
    tiles.on('tileload', () => { hasTiles = true; message.textContent = ''; });
    tiles.on('tileerror', () => {
        if (!hasTiles) message.textContent = 'Map tiles are unavailable. City markers and readings are still available.';
    });
    tiles.addTo(map);

    const markers = cities.map((city, index) => {
        const available = hasReading(city);
        const marker = leaflet.marker([city.lat, city.lon], {
            icon: leaflet.divIcon({ className: 'map-pin', iconSize: [40, 40], html: available ? `${city.temp}°` : '—' }),
            title: `${city.city}: ${available ? `${city.temp}°C` : 'No reading'}`
        });
        const popup = element('div', undefined, 'map-popup');
        popup.append(element('strong', city.city), element('span', available ? `${city.temp}°C · ${city.description}` : 'No reading in this snapshot'));
        marker.addTo(map).bindPopup(popup).on('click', () => selectCity(index));
        marker.getElement()?.setAttribute('aria-label', marker.options.title);
        return marker;
    });

    byId('reset-map').hidden = false;
    byId('reset-map').addEventListener('click', reset);
    message.textContent = '';
    let lastWidth = surface.clientWidth;
    new ResizeObserver(() => {
        const width = surface.clientWidth;
        map.invalidateSize({ pan: false });
        if (width !== lastWidth) { lastWidth = width; reset(); }
    }).observe(surface);
    return (index) => {
        map.setView(markers[index].getLatLng(), 11, { animate: false });
        markers[index].openPopup();
    };
}

async function load() {
    let snapshot;
    try {
        const response = await fetch('dashboard/weather.json', { cache: 'no-cache' });
        if (!response.ok) throw new Error('Snapshot unavailable');
        snapshot = await response.json();
        if (!snapshot.cities?.length || !snapshot.cities.every((city) => typeof city?.city === 'string'
            && Number.isFinite(city.lat) && Number.isFinite(city.lon))) throw new Error('Invalid snapshot');
    } catch {
        status('error', 'Snapshot unavailable', 'City readings could not be loaded.');
        byId('load-error').hidden = false;
        byId('load-error').textContent = 'The weather snapshot could not be loaded. Try reloading the page in a moment.';
        byId('map-status').textContent = 'The map is unavailable without city locations.';
        return;
    }

    const { cities } = snapshot;
    const readings = cities.filter(hasReading);
    showSnapshot(snapshot, cities, readings);
    const temperatures = readings.map(({ temp }) => temp);
    showBars('temperature-bars', readings, 'temp', '°C', Math.min(0, ...temperatures), Math.max(40, ...temperatures));
    showBars('humidity-bars', readings, 'humidity', '%', 0, 100);

    let showMapCity;
    const buttons = cities.map((city, index) => {
        const button = element('button', undefined, 'city-button');
        const name = element('span', city.city);
        const available = hasReading(city);
        name.append(element('small', available ? city.description : 'No reading'));
        button.type = 'button';
        button.setAttribute('aria-pressed', 'false');
        button.append(name, element('strong', available ? `${city.temp}°C` : '—'));
        button.addEventListener('click', () => {
            selectCity(index);
            showMapCity?.(index);
        });
        return button;
    });

    function selectCity(index) {
        buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
        showDetail(cities[index]);
    }

    byId('cities').replaceChildren(...buttons.map((button) => {
        const item = element('li');
        item.append(button);
        return item;
    }));
    selectCity(Math.max(0, cities.findIndex(hasReading)));
    showMapCity = initMap(cities, selectCity);
}

load();
