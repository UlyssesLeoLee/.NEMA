(()=>{
  'use strict';
  const data = window.NEMA_RULES || [];
  const body = document.getElementById('matrixRows');
  const dialog = document.getElementById('ruleDialog');
  let selected = null;
  let filter = (new URLSearchParams(location.search).get('mode') || 'table');

  const colClasses = ['col-syntax', 'col-desc', 'col-example', 'col-reason', 'col-anomaly', 'col-variant', 'col-render'];

  function td(v, asCode = false, colClass = '') {
    const e = document.createElement('td');
    if (colClass) e.className = colClass;
    if (asCode) {
      const c = document.createElement('code');
      c.textContent = v;
      e.append(c);
    } else {
      e.textContent = v;
    }
    return e;
  }

  function render() {
    const q = document.getElementById('search').value.toLowerCase().trim();
    body.replaceChildren();
    const list = data.filter(r => (filter === 'all' || r.mode === filter) && (!q || Object.values(r).join(' ').toLowerCase().includes(q)));
    const frag = document.createDocumentFragment();

    for (const r of list) {
      const tr = document.createElement('tr');
      tr.tabIndex = 0;
      tr.setAttribute('role', 'button');
      tr.setAttribute('aria-label', '查看 ' + r.label + ' 的详细例子');

      [r.syntax, r.description, r.example, r.reason, r.anomaly, r.variant, r.render].forEach((v, i) => {
        tr.append(td(v, i === 0 || i === 2 || i === 5, colClasses[i]));
      });

      const s = document.createElement('span');
      s.className = 'ng-status ' + r.status;
      s.textContent = r.status === 'valid' ? '有效' : r.status === 'error' ? '错误案例' : '候选未实现';
      tr.lastElementChild.append(document.createElement('br'), s);

      tr.addEventListener('click', () => open(r));
      tr.addEventListener('keydown', ev => {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          open(r);
        }
      });
      frag.append(tr);
    }
    body.append(frag);
    document.getElementById('count').textContent = list.length + ' 条变体 / 全部 ' + data.length;
  }

  function open(r) {
    selected = r;
    document.getElementById('dialogTitle').textContent = r.label + ' · ' + r.syntax;
    document.getElementById('dialogDesc').textContent = r.description + '；设计理由：' + r.reason;
    document.getElementById('dialogCode').textContent = r.variant;
    document.getElementById('dialogRisk').textContent = '防范异常：' + r.anomaly + '。本条预期：' + r.render;
    let result = '';
    if (r.status === 'proposal') {
      result = '候选语法：尚未由正式 .nemat Codec 实现\n预期：' + r.render;
    } else {
      try {
        const ast = window.NemaStrict.parse(r.variant);
        result = '解析成功\n' + JSON.stringify(ast, null, 2);
      } catch (e) {
        result = '解析错误（预期 ' + r.status + '）\n' + e.message;
      }
    }
    document.getElementById('dialogAST').textContent = result;
    document.getElementById('runRule').disabled = r.status === 'proposal';
    dialog.showModal();
  }

  document.querySelectorAll('[data-filter]').forEach(b => b.addEventListener('click', () => {
    filter = b.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach(x => {
      x.classList.toggle('active', x === b);
      x.setAttribute('aria-selected', String(x === b));
    });
    render();
  }));

  document.querySelectorAll('[data-filter]').forEach(b => {
    b.classList.toggle('active', b.dataset.filter === filter);
    b.setAttribute('aria-selected', String(b.dataset.filter === filter));
  });

  document.getElementById('search').addEventListener('input', render);
  document.getElementById('dialogClose').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => {
    if (e.target === dialog) dialog.close();
  });
  document.getElementById('copyRule').addEventListener('click', () => selected && window.NEMA_UI.copy(selected.variant));
  document.getElementById('runRule').addEventListener('click', () => {
    if (!selected) return;
    location.href = 'playground.html?case=' + encodeURIComponent(selected.id);
  });

  render();
})();
