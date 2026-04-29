/**
 * Leaflet 지도 관리 스크립트
 */

// ── 상태 변수 ────────────────────────────────────────
var map;
var piMarkers = [];
var midpointMarkers = [];
var segmentLines = [];
var piLineLayer = null;
var markerMap = {}; // { index: marker }

// 드래그 상태 관리
var isDragging = false;
var dragThrottleTimer = null;

// ── 지도 초기화 ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    map = L.map('map').setView([37.5665, 126.9780], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    // 지도 클릭 이벤트
    map.on('click', function(e) {
        if (isDragging) return;
        window.pywebview?.api?.on_map_click(e.latlng.lat, e.latlng.lng);
    });
});

// ── Python 통신 준비 완료 ────────────────────────────
window.addEventListener('pywebviewready', function() {
    window.pywebview.api.on_map_ready();
});

// ── 유틸리티 및 이벤트 바인딩 ───────────────────────
function bindMarkerEvents(marker, type) {
    marker.on('dragstart', function() {
        isDragging = true;
        if (type === 'pi') {
            window.pywebview?.api?.on_pi_drag_start(this.pointIndex);
        } else {
            window.pywebview?.api?.on_mid_drag_start(this.midIndex);
        }
    });

    marker.on('drag', function(e) {
        var ll = e.target.getLatLng();
        throttledDragCall(this.pointIndex || this.midIndex, ll.lat, ll.lng, type);
    });

    marker.on('dragend', function(e) {
        isDragging = false;
        if (dragThrottleTimer) {
            clearTimeout(dragThrottleTimer);
            dragThrottleTimer = null;
        }
        var ll = e.target.getLatLng();
        if (type === 'pi') {
            window.pywebview?.api?.on_pi_drag_end(this.pointIndex, ll.lat, ll.lng);
        } else {
            window.pywebview?.api?.on_mid_drag_end(this.midIndex, ll.lat, ll.lng);
        }
    });
}

function throttledDragCall(index, lat, lng, type) {
    if (!isDragging || dragThrottleTimer) return;

    dragThrottleTimer = setTimeout(function() {
        dragThrottleTimer = null;
        if (isDragging && window.pywebview?.api) {
            if (type === 'pi') {
                window.pywebview.api.on_pi_dragging(index, lat, lng);
            } else {
                window.pywebview.api.on_mid_dragging?.(index, lat, lng);
            }
        }
    }, 40);
}

// ── 렌더링 API (Python에서 호출) ─────────────────────

/** 전체 재렌더링 */
window.renderAll = function(dataStr) {
    var data = typeof dataStr === "string" ? JSON.parse(dataStr) : dataStr;

    // 기존 요소 초기화
    piMarkers.forEach(m => m.remove());
    midpointMarkers.forEach(m => m.remove());
    segmentLines.forEach(l => l.remove());
    if (piLineLayer) piLineLayer.remove();

    piMarkers = [];
    midpointMarkers = [];
    segmentLines = [];
    markerMap = {};

    // 1. PI 보조선 (점선)
    if (data.pi_line && data.pi_line.length > 1) {
        piLineLayer = L.polyline(data.pi_line, {
            color: 'red', weight: 1, dashArray: '5, 5', interactive: false
        }).addTo(map);
    }

    // 2. 세그먼트 (곡선)
    if (data.segments) {
        data.segments.forEach(function(seg) {
            var poly = L.polyline(seg.path, {
                color: seg.color || 'cyan', weight: 3, opacity: 0.8, interactive: false
            }).addTo(map);
            segmentLines.push(poly);
        });
    }

    // 3. PI 마커
    if (data.pi) {
        data.pi.forEach(function(p) {
            var marker = L.marker([p.lat, p.lng], { draggable: true }).addTo(map);
            marker.bindTooltip(p.label, { permanent: true, direction: 'top', offset: [0, -10] });
            marker.pointIndex = p.index;
            markerMap[p.index] = marker;
            bindMarkerEvents(marker, 'pi');
            piMarkers.push(marker);
        });
    }

    // 4. Midpoint 마커
    if (data.midpoints) {
        data.midpoints.forEach(function(m) {
            var dragM = L.marker([m.lat, m.lng], {
                icon: L.divIcon({
                    className: 'mid-icon',
                    html: '<div class="mid-icon-inner"></div>',
                    iconSize: [10, 10],
                    iconAnchor: [5, 5]
                }),
                draggable: true
            }).addTo(map);
            dragM.midIndex = m.index;
            bindMarkerEvents(dragM, 'midpoint');
            midpointMarkers.push(dragM);
        });
    }
};

/** 드래그 중 선형만 업데이트 */
window.updatePathsOnly = function(dataStr) {
    var data = typeof dataStr === "string" ? JSON.parse(dataStr) : dataStr;
    segmentLines.forEach(l => l.remove());
    segmentLines = [];

    if (data.segments) {
        data.segments.forEach(function(seg) {
            var poly = L.polyline(seg.path, {
                color: 'yellow', weight: 2, dashArray: '5, 10', interactive: false
            }).addTo(map);
            segmentLines.push(poly);
        });
    }
};

/** 드래그 종료 후 확정 렌더링 */
window.updateAfterDrag = function(dataStr) {
    // 마커 위치 및 선형 스타일 복구
    window.renderAll(dataStr);
};