const API = "https://forma-secondhand-shop-clothes.onrender.com";
let token = localStorage.getItem("token");

// ---------- toast ----------

function toast(msg, isErr = false) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.className = "toast show" + (isErr ? " err" : "");
  setTimeout(() => { el.className = "toast"; }, 2800);
}

// ---------- api helper ----------

async function api(path, options = {}) {
  const headers = options.headers || {};
  headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(API + path, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------- auth ----------

async function getCurrentUser() {
  if (!token) return null;
  try {
    return await api("/auth/me");
  } catch {
    token = null;
    localStorage.removeItem("token");
    return null;
  }
}

function logout() {
  token = null;
  localStorage.removeItem("token");
  window.location.href = "index.html";
}

// ---------- cart (persisted in localStorage, живет между страницами) ----------

function getCart() {
  try {
    return JSON.parse(localStorage.getItem("cart") || "[]");
  } catch {
    return [];
  }
}

function saveCart(cart) {
  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartBadge();
}

function addToCart(productId, name, price) {
  const cart = getCart();
  const existing = cart.find(i => i.product_id === productId);
  if (existing) existing.quantity += 1;
  else cart.push({ product_id: productId, name, price, quantity: 1 });
  saveCart(cart);
  toast(`${name} — в корзине`);
}

function removeFromCart(productId) {
  saveCart(getCart().filter(i => i.product_id !== productId));
}

function updateCartQuantity(productId, quantity) {
  const cart = getCart();
  const item = cart.find(i => i.product_id === productId);
  if (!item) return;
  if (quantity <= 0) {
    saveCart(cart.filter(i => i.product_id !== productId));
  } else {
    item.quantity = quantity;
    saveCart(cart);
  }
}

function updateCartBadge() {
  const badge = document.getElementById("cart-count");
  if (!badge) return;
  const count = getCart().reduce((sum, i) => sum + i.quantity, 0);
  badge.textContent = count;
}

// ---------- telegram manager setting ----------
// хранится локально в браузере, настраивается из admin.html
// временное решение для демо, в проде это была бы таблица settings в базе

function getManagerUsername() {
  return localStorage.getItem("manager_username") || "your_manager";
}

function setManagerUsername(username) {
  localStorage.setItem("manager_username", username);
}

// ---------- shared header ----------
// рендерит шапку сайта одинаково на всех страницах

async function renderHeader() {
  const user = await getCurrentUser();
  const container = document.getElementById("site-header");
  if (!container) return;

  const isAdmin = user && user.role === "admin";

  container.innerHTML = `
    <div class="wrap header-row">
      <a href="index.html" class="wordmark">Archive</a>
      <nav class="account-nav">
        ${isAdmin ? `<a href="admin.html" class="btn-text">Админка</a>` : ""}
        ${user ? `<a href="favorites.html" class="btn-text">Избранное</a>` : ""}
        ${user ? `<a href="outfit.html" class="btn-text">Собрать образ</a>` : ""}
        <a href="cart.html" class="btn-text">Корзина (<span id="cart-count">0</span>)</a>
        ${user
          ? `<span class="muted">${escapeHtml(user.email)}</span>
             <span class="role-tag">${isAdmin ? "admin" : "покупатель"}</span>
             <button class="btn-text" onclick="logout()">Выйти</button>`
          : `<a href="login.html" class="btn-text">Войти</a>`
        }
      </nav>
    </div>
  `;

  updateCartBadge();
  return user;
}