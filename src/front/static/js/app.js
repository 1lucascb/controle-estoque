const page = document.body.dataset.page;
const state = { products: [], users: [], logs: [], categories: [] };
const charts = {};
const chartModes = { category: 'category', product: 'product' };

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[char]));
const money = value => `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;
const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
const date = value => {
    if (!value) return '-';

    const serverValue = String(value);
    const hasTimeZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(serverValue);
    const instant = new Date(hasTimeZone ? serverValue : `${serverValue}Z`);

    if (Number.isNaN(instant.getTime())) return '-';
    return instant.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short', timeZone: userTimeZone });
};
const icon = name => `<i data-lucide="${name}"></i>`;

async function request(url, options = {}) {
    const response = await fetch(url, { credentials: 'same-origin', headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
    if (response.status === 401) { window.location.href = '/auth/login.html'; throw new Error('Sessao expirada.'); }
    if (!response.ok) { let message = `Erro ${response.status}`; try { message = (await response.json()).detail || message; } catch (_) { } throw new Error(message); }
    return response.status === 204 ? null : response.json();
}

function refreshIcons() { if (window.lucide) window.lucide.createIcons(); }
function showToast(message, type = 'success') { const toast = $('#toast'); toast.textContent = message; toast.className = `toast show ${type}`; setTimeout(() => toast.className = 'toast', 3500); }
function setLoading(target, message = 'Carregando dados...') { const content = `<div class="empty-state">${icon('loader-circle')}<p>${message}</p></div>`; target.innerHTML = target.tagName === 'TBODY' ? `<tr><td colspan="${target.dataset.columns || 1}">${content}</td></tr>` : content; refreshIcons(); }
function openModal(id, title) { $(`#${id} .modal-title`).textContent = title; $(`#${id}`).classList.add('open'); $(`#${id} input, #${id} textarea, #${id} select`)?.focus(); }
function closeModal(id) { $(`#${id}`).classList.remove('open'); }
function bindModal(id) { const modal = $(`#${id}`); $(`[data-close="${id}"]`)?.addEventListener('click', () => closeModal(id)); modal.addEventListener('click', event => { if (event.target === modal) closeModal(id); }); }
function bindLogout() { const footer = $('.sidebar-footer'); if (!footer) return; footer.insertAdjacentHTML('beforeend', `<button class="logout-btn" type="button" data-logout>${icon('log-out')}<span>Sair</span></button>`); $('[data-logout]').addEventListener('click', async event => { const button = event.currentTarget; button.disabled = true; try { await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'same-origin' }); } finally { window.location.href = '/auth/login.html'; } }); }

async function loadProducts() { state.products = await request('/api/v1/products'); return state.products; }
async function loadUsers() { state.users = await request('/api/v1/users'); return state.users; }
async function loadLogs() { state.logs = await request('/api/v1/stock-logs'); return state.logs; }
async function loadCategories() { state.categories = await request('/api/v1/categories'); return state.categories; }
function categoryName(categoryId) { return state.categories.find(category => category.id == categoryId)?.name || 'Geral'; }

function productStatus(product) { return product.is_low_stock ? '<span class="badge badge-warning">Estoque baixo</span>' : '<span class="badge badge-success">Disponivel</span>'; }
function renderProductRows(products = state.products) {
    const body = $('#product-table-body');
    body.innerHTML = products.length ? products.map(product => `<tr><td><strong>${escapeHtml(product.name)}</strong><br><small>${escapeHtml(categoryName(product.category_id))}</small></td><td>${product.current_amount}</td><td>${product.min_stock_threshold}</td><td>${productStatus(product)}</td><td><div class="actions"><button class="icon-btn" title="Ajustar estoque" data-stock="${product.id}">${icon('package-plus')}</button><button class="icon-btn" title="Editar produto" data-edit-product="${product.id}">${icon('pencil')}</button><button class="icon-btn" title="Excluir produto" data-delete-product="${product.id}">${icon('trash-2')}</button></div></td></tr>`).join('') : '<tr><td colspan="5"><div class="empty-state">Nenhum produto encontrado.</div></td></tr>';
    refreshIcons();
}
function fillProductForm(product = {}) { const form = $('#product-form'); form.reset(); form.elements.productId.value = product.id || ''; form.elements.name.value = product.name || ''; form.elements.description.value = product.description || ''; form.elements.category_id.value = product.category_id || ''; form.elements.current_amount.value = product.current_amount ?? 0; form.elements.min_stock_threshold.value = product.min_stock_threshold ?? 5; form.elements.image_path.value = product.image_path || ''; }
function renderCategoryOptions() { $('#category_id').innerHTML = '<option value="">Selecione uma categoria</option>' + state.categories.map(category => `<option value="${category.id}">${escapeHtml(category.name)}</option>`).join(''); }
async function initProducts() {
    setLoading($('#product-table-body')); try { await Promise.all([loadCategories(), loadProducts()]); renderCategoryOptions(); renderProductRows(); } catch (error) { $('#product-table-body').innerHTML = `<tr><td colspan="5"><div class="empty-state">${escapeHtml(error.message)}</div></td></tr>`; }
    bindModal('product-modal'); bindModal('stock-modal');
    $('#new-product').addEventListener('click', () => { fillProductForm(); openModal('product-modal', 'Novo produto'); });
    $('#product-form').addEventListener('submit', async event => { event.preventDefault(); const form = event.currentTarget; const id = form.elements.productId.value; const payload = { name: form.elements.name.value, description: form.elements.description.value || null, category_id: Number(form.elements.category_id.value), current_amount: Number(form.elements.current_amount.value), min_stock_threshold: Number(form.elements.min_stock_threshold.value), image_path: form.elements.image_path.value || null }; try { await request(id ? `/api/v1/products/${id}` : '/api/v1/products', { method: id ? 'PUT' : 'POST', body: JSON.stringify(payload) }); closeModal('product-modal'); await loadProducts(); renderProductRows(); showToast(id ? 'Produto atualizado.' : 'Produto criado.'); } catch (error) { showToast(error.message, 'error'); } });
    $('#stock-form').addEventListener('submit', async event => { event.preventDefault(); const form = event.currentTarget; try { await request(`/api/v1/products/${form.elements.productId.value}/stock`, { method: 'PATCH', body: JSON.stringify({ change_amount: Number(form.elements.change_amount.value), reason: form.elements.reason.value || null }) }); closeModal('stock-modal'); await loadProducts(); renderProductRows(); showToast('Estoque ajustado.'); } catch (error) { showToast(error.message, 'error'); } });
    $('#product-table-body').addEventListener('click', async event => { const edit = event.target.closest('[data-edit-product]'); const stock = event.target.closest('[data-stock]'); const remove = event.target.closest('[data-delete-product]'); if (edit) { fillProductForm(state.products.find(item => item.id == edit.dataset.editProduct)); openModal('product-modal', 'Editar produto'); } if (stock) { $('#stock-form').reset(); $('#stock-form').elements.productId.value = stock.dataset.stock; openModal('stock-modal', 'Ajustar estoque'); } if (remove && confirm('Excluir este produto?')) { try { await request(`/api/v1/products/${remove.dataset.deleteProduct}`, { method: 'DELETE' }); await loadProducts(); renderProductRows(); showToast('Produto excluido.'); } catch (error) { showToast(error.message, 'error'); } } });
    $('#product-search').addEventListener('input', event => { const term = event.target.value.toLowerCase(); renderProductRows(state.products.filter(product => `${product.name} ${categoryName(product.category_id)}`.toLowerCase().includes(term))); });
}

function renderCategoryRows() { const body = $('#category-table-body'); body.innerHTML = state.categories.map(category => `<tr><td>${escapeHtml(category.name)}</td><td><button class="icon-btn" title="Excluir categoria" data-delete-category="${category.id}">${icon('trash-2')}</button></td></tr>`).join('') || '<tr><td colspan="2"><div class="empty-state">Nenhuma categoria encontrada.</div></td></tr>'; refreshIcons(); }
async function initCategories() { setLoading($('#category-table-body')); try { await loadCategories(); renderCategoryRows(); } catch (error) { $('#category-table-body').innerHTML = `<tr><td colspan="2"><div class="empty-state">${escapeHtml(error.message)}</div></td></tr>`; } bindModal('category-modal'); $('#new-category').addEventListener('click', () => { $('#category-form').reset(); openModal('category-modal', 'Nova categoria'); }); $('#category-form').addEventListener('submit', async event => { event.preventDefault(); try { await request('/api/v1/categories', { method: 'POST', body: JSON.stringify({ name: event.currentTarget.elements.name.value }) }); closeModal('category-modal'); await loadCategories(); renderCategoryRows(); showToast('Categoria criada.'); } catch (error) { showToast(error.message, 'error'); } }); $('#category-table-body').addEventListener('click', async event => { const remove = event.target.closest('[data-delete-category]'); if (remove && confirm('Excluir esta categoria?')) { try { await request(`/api/v1/categories/${remove.dataset.deleteCategory}`, { method: 'DELETE' }); await loadCategories(); renderCategoryRows(); showToast('Categoria excluida.'); } catch (error) { showToast(error.message, 'error'); } } }); }

function renderUserRows(users = state.users) { const body = $('#user-table-body'); body.innerHTML = users.length ? users.map(user => `<tr><td><strong>${escapeHtml(user.full_name || user.username)}</strong><br><small>@${escapeHtml(user.username)}</small></td><td><span class="badge ${user.role === 'admin' ? 'badge-warning' : 'badge-neutral'}">${escapeHtml(user.role)}</span></td><td>${user.is_active ? '<span class="badge badge-success">Ativo</span>' : '<span class="badge badge-danger">Inativo</span>'}</td><td>${user.id}</td><td><button class="icon-btn" title="Excluir usuario" data-delete-user="${user.id}">${icon('trash-2')}</button></td></tr>`).join('') : '<tr><td colspan="5"><div class="empty-state">Nenhum usuario encontrado.</div></td></tr>'; refreshIcons(); }
async function initUsers() { setLoading($('#user-table-body')); try { await loadUsers(); renderUserRows(); } catch (error) { $('#user-table-body').innerHTML = `<tr><td colspan="5"><div class="empty-state">${escapeHtml(error.message)}</div></td></tr>`; } bindModal('user-modal'); $('#new-user').addEventListener('click', () => { $('#user-form').reset(); openModal('user-modal', 'Novo usuario'); }); $('#user-form').addEventListener('submit', async event => { event.preventDefault(); const form = event.currentTarget; try { await request('/api/v1/users', { method: 'POST', body: JSON.stringify({ username: form.elements.username.value, full_name: form.elements.full_name.value || null }) }); closeModal('user-modal'); await loadUsers(); renderUserRows(); showToast('Usuario criado.'); } catch (error) { showToast(error.message, 'error'); } }); $('#user-table-body').addEventListener('click', async event => { const remove = event.target.closest('[data-delete-user]'); if (remove && confirm('Excluir este usuario?')) { try { await request(`/api/v1/users/${remove.dataset.deleteUser}`, { method: 'DELETE' }); await loadUsers(); renderUserRows(); showToast('Usuario excluido.'); } catch (error) { showToast(error.message, 'error'); } } }); }

async function initChangePassword() {
    const form = $('#change-password-form');
    form.addEventListener('submit', async event => {
        event.preventDefault();
        const button = form.querySelector('button[type="submit"]');
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());
        button.disabled = true;
        try {
            await request('/api/v1/auth/change-password', { method: 'POST', body: JSON.stringify(payload) });
            form.reset();
            showToast('Senha alterada com sucesso.');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            button.disabled = false;
        }
    });
}

async function initLogs() { setLoading($('#log-table-body')); try { await loadLogs(); renderLogs(); } catch (error) { $('#log-table-body').innerHTML = `<tr><td colspan="6"><div class="empty-state">${escapeHtml(error.message)}</div></td></tr>`; } $('#log-search').addEventListener('input', renderLogs); }
function renderLogs() { const term = $('#log-search').value.toLowerCase(); const logs = state.logs.filter(log => `${log.product_name} ${log.user_name} ${log.reason || ''}`.toLowerCase().includes(term)); $('#log-table-body').innerHTML = logs.length ? logs.map(log => `<tr><td>${date(log.created_at)}</td><td><strong>${escapeHtml(log.product_name)}</strong></td><td>${escapeHtml(log.user_name)}</td><td><span class="badge ${log.difference >= 0 ? 'badge-success' : 'badge-danger'}">${log.difference >= 0 ? '+' : ''}${log.difference}</span></td><td>${log.previous_amount} -> ${log.new_amount}</td><td>${escapeHtml(log.reason || 'Sem motivo')}</td></tr>`).join('') : '<tr><td colspan="6"><div class="empty-state">Nenhuma movimentacao encontrada.</div></td></tr>'; refreshIcons(); }

function chartColors(count) { return Array.from({ length: count }, (_, index) => `hsl(${(index * 137.5 + 200) % 360} 62% 48%)`); }
function renderDashboardCharts() {
    const totalsBy = dimension => state.products.reduce((totals, product) => {
        const name = dimension === 'category' ? categoryName(product.category_id) : product.name;
        if (!totals[name]) totals[name] = { amount: 0, hasLowStock: false };
        totals[name].amount += product.current_amount;
        totals[name].hasLowStock ||= product.is_low_stock;
        return totals;
    }, {});
    const doughnutTotals = totalsBy(chartModes.category);
    const barTotals = totalsBy(chartModes.product);
    const doughnutLabels = Object.keys(doughnutTotals);
    const barLabels = Object.keys(barTotals);
    const hasProducts = state.products.length > 0;
    $('#stock-category-empty').hidden = hasProducts;
    $('#product-stock-empty').hidden = hasProducts;
    $('#category-chart-title').textContent = `Estoque por ${chartModes.category === 'category' ? 'categoria' : 'produto'}`;
    $('#category-chart-subtitle').textContent = `Distribuicao do saldo atual por ${chartModes.category === 'category' ? 'categoria' : 'produto'}.`;
    $('#product-chart-title').textContent = `Saldo por ${chartModes.product === 'category' ? 'categoria' : 'produto'}`;
    $('#product-chart-subtitle').textContent = `Quantidade disponivel por ${chartModes.product === 'category' ? 'categoria' : 'produto'}.`;
    if (!window.Chart || !hasProducts) return;
    charts.category?.destroy();
    charts.product?.destroy();
    charts.category = new Chart($('#stock-category-chart'), {
        type: 'doughnut',
        data: { labels: doughnutLabels, datasets: [{ data: doughnutLabels.map(label => doughnutTotals[label].amount), backgroundColor: doughnutLabels.map((label, index) => doughnutTotals[label].hasLowStock ? '#dd6b20' : chartColors(doughnutLabels.length)[index]), borderWidth: 2, borderColor: '#ffffff' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
    });
    charts.product = new Chart($('#product-stock-chart'), {
        type: 'bar',
        data: { labels: barLabels, datasets: [{ label: 'Unidades', data: barLabels.map(label => barTotals[label].amount), backgroundColor: barLabels.map((label, index) => barTotals[label].hasLowStock ? '#dd6b20' : chartColors(barLabels.length)[index]), borderRadius: 4, maxBarThickness: 42 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }, plugins: { legend: { display: false } } },
    });
}
async function initDashboard() { try { await Promise.all([loadProducts(), loadUsers(), loadLogs(), loadCategories()]); $('#stat-products').textContent = state.products.length; $('#stat-low').textContent = state.products.filter(item => item.is_low_stock).length; $('#stat-users').textContent = state.users.length; $('#stat-movements').textContent = state.logs.length; renderDashboardCharts(); $('#category-chart-mode').addEventListener('change', event => { chartModes.category = event.target.value; renderDashboardCharts(); }); $('#product-chart-mode').addEventListener('change', event => { chartModes.product = event.target.value; renderDashboardCharts(); }); $('#low-stock-list').innerHTML = state.products.filter(item => item.is_low_stock).slice(0, 5).map(item => `<div class="list-row"><span><strong>${escapeHtml(item.name)}</strong><small>${item.current_amount} unidades disponiveis</small></span>${productStatus(item)}</div>`).join('') || '<div class="empty-state">Tudo em ordem por aqui.</div>'; $('#recent-list').innerHTML = state.logs.slice(0, 5).map(log => `<div class="list-row"><span><strong>${escapeHtml(log.product_name)}</strong><small>${escapeHtml(log.user_name)} - ${date(log.created_at)}</small></span><b class="${log.difference >= 0 ? 'positive' : 'negative'}">${log.difference >= 0 ? '+' : ''}${log.difference}</b></div>`).join('') || '<div class="empty-state">Nenhuma movimentacao recente.</div>'; refreshIcons(); } catch (error) { showToast(error.message, 'error'); } }

document.addEventListener('DOMContentLoaded', () => { $$('.nav-link').forEach(link => link.classList.toggle('active', link.dataset.page === page)); bindLogout(); $$('.modal-backdrop').forEach(modal => modal.addEventListener('keydown', event => { if (event.key === 'Escape') modal.classList.remove('open'); })); if (page === 'dashboard') initDashboard(); if (page === 'products') initProducts(); if (page === 'categories') initCategories(); if (page === 'logs') initLogs(); if (page === 'users') initUsers(); if (page === 'change-password') initChangePassword(); refreshIcons(); });