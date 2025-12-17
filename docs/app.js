async function loadLatest() {
  const container = document.getElementById('metrics');
  container.innerHTML = '<p>Loading...</p>';

  try {
    const res = await fetch('data/latest.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error(`Failed to load latest.json: ${res.status}`);
    const data = await res.json();
    renderMetrics(container, data);
  } catch (err) {
    container.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

function metricLabel(key) {
  const labels = {
    metr_time_horizon_p50_minutes: 'METR time horizon (50%)',
    metr_time_horizon_p80_minutes: 'METR time horizon (80%)',
    metr_time_horizon_p50_ci_low_minutes: 'METR time horizon (50%) CI low',
    metr_time_horizon_p50_ci_high_minutes: 'METR time horizon (50%) CI high',
    metr_time_horizon_p80_ci_low_minutes: 'METR time horizon (80%) CI low',
    metr_time_horizon_p80_ci_high_minutes: 'METR time horizon (80%) CI high',
    gdpval_table2_win_rate_percent: 'GDPval win rate',
    arc_agi_2_private_sota_percent: 'ARC-AGI-2 private SOTA',
    arc_agi_2_private_sota_cost_per_task_usd: 'ARC-AGI-2 cost per task',
  };
  return labels[key] || key;
}

function metricFamily(key) {
  if (key.startsWith('metr_time_horizon')) return 'METR time horizon';
  if (key.startsWith('gdpval')) return 'GDPval Table 2';
  if (key.startsWith('arc_agi_2')) return 'ARC-AGI-2';
  return 'Other';
}

function renderMetrics(container, data) {
  const entries = Object.values(data || {});
  if (!entries.length) {
    container.innerHTML = '<p>No metrics have been recorded yet.</p>';
    return;
  }

  const grouped = entries.reduce((acc, item) => {
    const family = metricFamily(item.metric_key);
    acc[family] = acc[family] || [];
    acc[family].push(item);
    return acc;
  }, {});

  const wrapper = document.createElement('div');

  Object.entries(grouped).forEach(([family, metrics]) => {
    const section = document.createElement('div');
    section.innerHTML = `<h3>${family}</h3>`;

    const table = document.createElement('table');
    const thead = document.createElement('thead');
    thead.innerHTML = '<tr><th>Metric</th><th>Entity</th><th>Value</th><th>Last updated</th><th>Evidence</th></tr>';
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    metrics.forEach((m) => {
      const tr = document.createElement('tr');
      const unit = m.unit ? ` ${m.unit}` : '';
      tr.innerHTML = `
        <td>${metricLabel(m.metric_key)}</td>
        <td><span class="badge">${m.entity}</span></td>
        <td>${m.value}${unit}</td>
        <td>${m.timestamp || ''}</td>
        <td>
          <details class="details">
            <summary>View</summary>
            <div class="evidence">${m.evidence || ''}</div>
            <div class="source">Source: <a href="${m.url}" target="_blank" rel="noreferrer">${m.source}</a></div>
          </details>
        </td>`;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    section.appendChild(table);
    wrapper.appendChild(section);
  });

  container.innerHTML = '';
  container.appendChild(wrapper);
}

window.addEventListener('DOMContentLoaded', loadLatest);
