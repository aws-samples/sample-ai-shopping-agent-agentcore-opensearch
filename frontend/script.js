// Configuration - Connected to Real AgentCore Agent!
// Uses relative URL so it works behind ALB or locally
const API_ENDPOINT = '/chat';

// Sample Product Data
const productDatabase = {
    electronics: [
        { id: 1, name: 'Wireless Headphones', price: 79.99, category: 'Electronics', image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop' },
        { id: 2, name: 'Smart Watch', price: 199.99, category: 'Electronics', image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop' },
        { id: 3, name: 'Bluetooth Speaker', price: 49.99, category: 'Electronics', image: 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop' },
        { id: 4, name: 'Laptop Stand', price: 39.99, category: 'Electronics', image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=400&fit=crop' }
    ],
    beauty: [
        { id: 5, name: 'Facial Serum', price: 45.99, category: 'Beauty', image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=400&fit=crop' },
        { id: 6, name: 'Moisturizer', price: 32.99, category: 'Beauty', image: 'https://images.unsplash.com/photo-1556228852-80837c0f46bb?w=400&h=400&fit=crop' },
        { id: 7, name: 'Face Mask Set', price: 24.99, category: 'Beauty', image: 'https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400&h=400&fit=crop' }
    ],
    fashion: [
        { id: 8, name: 'Black Midi Skirt', price: 58.99, category: 'Fashion', image: 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400&h=400&fit=crop' },
        { id: 9, name: 'Polka Dot Dress', price: 74.99, category: 'Fashion', image: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=400&fit=crop' },
        { id: 10, name: 'Casual Blazer', price: 89.99, category: 'Fashion', image: 'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=400&h=400&fit=crop' },
        { id: 11, name: 'Summer Sandals', price: 45.99, category: 'Fashion', image: 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&h=400&fit=crop' }
    ],
    home: [
        { id: 12, name: 'Table Lamp', price: 65.99, category: 'Home', image: 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop' },
        { id: 13, name: 'Throw Pillows', price: 29.99, category: 'Home', image: 'https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=400&h=400&fit=crop' },
        { id: 14, name: 'Wall Clock', price: 42.99, category: 'Home', image: 'https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=400&h=400&fit=crop' }
    ],
    books: [
        { id: 15, name: 'Mystery Novel', price: 14.99, category: 'Books', image: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=400&fit=crop' },
        { id: 16, name: 'Cookbook', price: 24.99, category: 'Books', image: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=400&fit=crop' }
    ],
    grocery: [
        { id: 17, name: 'Organic Coffee', price: 18.99, category: 'Grocery', image: 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop' },
        { id: 18, name: 'Green Tea', price: 12.99, category: 'Grocery', image: 'https://images.unsplash.com/photo-1563822249366-b6ebbc03446c?w=400&h=400&fit=crop' }
    ],
    jewelry: [
        { id: 19, name: 'Silver Necklace', price: 89.99, category: 'Jewelry', image: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=400&h=400&fit=crop' },
        { id: 20, name: 'Gold Earrings', price: 129.99, category: 'Jewelry', image: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400&h=400&fit=crop' }
    ]
};

// State Management
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const scrollTopBtn = document.getElementById('scrollTopBtn');
const cartBtn = document.getElementById('cartBtn');
const wishlistBtn = document.getElementById('wishlistBtn');
const cartPanel = document.getElementById('cartPanel');
const wishlistPanel = document.getElementById('wishlistPanel');
const overlay = document.getElementById('overlay');
const closeCartBtn = document.getElementById('closeCartBtn');
const closeWishlistBtn = document.getElementById('closeWishlistBtn');
const navLinks = document.querySelectorAll('.nav-link');

// AI Response Templates
const responseTemplates = {
    greeting: "Hello! How can I help you find the perfect product today?",
    cart: "Let me show you what's in your cart.",
    wishlist: "Here are your saved items.",
    thanks: "You're welcome! Is there anything else I can help you with?",
    goodbye: "Thank you for shopping with us! Have a great day!",
    unknown: "I'd be happy to help you find what you're looking for. Could you tell me more about what you need?"
};

// Initialize
updateCartCount();
updateWishlistCount();

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

clearBtn.addEventListener('click', clearChat);
scrollTopBtn.addEventListener('click', () => {
    chatContainer.scrollTop = 0;
});

cartBtn.addEventListener('click', () => openPanel(cartPanel));
wishlistBtn.addEventListener('click', () => openPanel(wishlistPanel));
closeCartBtn.addEventListener('click', () => closePanel(cartPanel));
closeWishlistBtn.addEventListener('click', () => closePanel(wishlistPanel));
overlay.addEventListener('click', closeAllPanels);

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        const category = link.dataset.category;
        handleCategoryClick(category);
    });
});

// Main Functions
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Display user message
    addMessage(message, 'user');
    userInput.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Check if API is configured
    if (!API_ENDPOINT || API_ENDPOINT === 'YOUR_API_GATEWAY_URL_HERE') {
        // Fallback to mock responses if API not configured
        setTimeout(() => {
            hideTypingIndicator();
            const response = generateResponse(message);
            addMessage(response.text, 'assistant');
            
            if (response.products) {
                displayProducts(response.products);
            }
            
            scrollToBottom();
        }, 1500);
        return;
    }

    // Call the real API with extended timeout
    try {
        const userId = 'anonymous'; // Can be extended to support user login
        
        // Create AbortController for timeout management (2 minutes)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: userId
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId); // Clear timeout if request completes
        const data = await response.json();
        
        hideTypingIndicator();
        
        if (data.success && data.response) {
            addMessage(data.response, 'assistant');
            
            // Extract product data if present
            const { text, products } = extractProductDataFromResponse(data.response);
            if (products && products.length > 0) {
                displayProducts(products);
            }
        } else {
            addMessage(data.error || 'Sorry, I encountered an error. Please try again.', 'assistant');
        }
        
        scrollToBottom();
        
    } catch (error) {
        console.error('API Error:', error);
        hideTypingIndicator();
        addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'assistant');
        scrollToBottom();
    }
}

// Helper function to extract product data from agent response
function extractProductDataFromResponse(responseText) {
    try {
        // Look for RAW_PRODUCT_DATA pattern
        const rawDataMatch = responseText.match(/RAW_PRODUCT_DATA:\s*(\{.*\})/);
        if (rawDataMatch) {
            const jsonData = JSON.parse(rawDataMatch[1]);
            if (jsonData.success && jsonData.products) {
                const text = responseText.replace(/RAW_PRODUCT_DATA:.*$/,  '').trim();
                return { text, products: jsonData.products };
            }
        }
    } catch (e) {
        console.log('No product data found in response');
    }
    
    return { text: responseText, products: null };
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Render markdown for assistant messages, plain text for user
    if (type === 'assistant' && typeof marked !== 'undefined') {
        let html = marked.parse(text);
        
        // Remove "Image:" labels since we render actual images
        html = html.replace(/Image:\s*/gi, '');
        
        // Convert image URLs (in links or plain text) to actual <img> tags with centered white card styling
        html = html.replace(
            /<a href="(https?:\/\/[^"]+\.(png|jpg|jpeg|gif|webp)[^"]*)"[^>]*>[^<]*<\/a>/gi,
            '<div style="text-align:center;background:#fff;padding:16px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin:12px 0;"><img src="$1" alt="Product" style="max-width:250px;max-height:300px;border-radius:8px;object-fit:contain;"></div>'
        );
        
        // Also catch bare image URLs that marked didn't linkify
        html = html.replace(
            /(?<!src="|href=")(https?:\/\/[^\s<"]+\.(png|jpg|jpeg|gif|webp)[^\s<"]*)/gi,
            '<div style="text-align:center;background:#fff;padding:16px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin:12px 0;"><img src="$1" alt="Product" style="max-width:250px;max-height:300px;border-radius:8px;object-fit:contain;"></div>'
        );
        
        // Remove bullet points from list items that contain images
        html = html.replace(/<li>([\s\S]*?)<div style="text-align:center/gi, '<li style="list-style:none;margin-left:-20px;">$1<div style="text-align:center');
        
        contentDiv.innerHTML = html;
    } else {
        contentDiv.innerHTML = `<p>${text}</p>`;
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message assistant-message typing-indicator';
    indicator.id = 'typing';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    chatContainer.appendChild(indicator);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing');
    if (indicator) indicator.remove();
}

function generateResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    // Check for cart-related queries
    if (lowerMessage.includes('cart') || lowerMessage.includes('basket')) {
        return {
            text: cart.length > 0 
                ? `You have ${cart.length} item(s) in your cart. Click the cart icon to view details!`
                : "Your cart is currently empty. Let me help you find something great!",
            products: null
        };
    }
    
    // Check for wishlist queries
    if (lowerMessage.includes('wishlist') || lowerMessage.includes('saved') || lowerMessage.includes('favorites')) {
        return {
            text: wishlist.length > 0
                ? `You have ${wishlist.length} item(s) in your wishlist. Would you like to see them?`
                : "Your wishlist is empty. When you find items you love, save them here!",
            products: null
        };
    }
    
    // Product search by category
    for (const [category, products] of Object.entries(productDatabase)) {
        if (lowerMessage.includes(category) || 
            lowerMessage.includes(category.slice(0, -1))) {
            return {
                text: `Great choice! Here are some ${category} items you might like:`,
                products: products
            };
        }
    }
    
    // Price-based search
    if (lowerMessage.includes('under') || lowerMessage.includes('less than') || lowerMessage.includes('below')) {
        const priceMatch = lowerMessage.match(/\$?(\d+)/);
        if (priceMatch) {
            const maxPrice = parseFloat(priceMatch[1]);
            const affordableProducts = Object.values(productDatabase)
                .flat()
                .filter(p => p.price <= maxPrice)
                .slice(0, 4);
            
            return {
                text: `I found these products under $${maxPrice}:`,
                products: affordableProducts
            };
        }
    }
    
    // Gift suggestions
    if (lowerMessage.includes('gift') || lowerMessage.includes('present')) {
        const giftProducts = [
            ...productDatabase.beauty.slice(0, 2),
            ...productDatabase.jewelry.slice(0, 2)
        ];
        return {
            text: "These would make wonderful gifts!",
            products: giftProducts
        };
    }
    
    // Greeting
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
        return {
            text: responseTemplates.greeting,
            products: productDatabase.fashion.slice(0, 3)
        };
    }
    
    // Thanks
    if (lowerMessage.includes('thank')) {
        return { text: responseTemplates.thanks, products: null };
    }
    
    // Default response with popular items
    return {
        text: "Let me show you some popular items that might interest you:",
        products: [
            ...productDatabase.fashion.slice(0, 2),
            ...productDatabase.electronics.slice(0, 2)
        ]
    };
}

function displayProducts(products) {
    const galleryDiv = document.createElement('div');
    galleryDiv.className = 'product-gallery';
    
    const scrollDiv = document.createElement('div');
    scrollDiv.className = 'product-scroll';
    
    products.forEach(product => {
        const card = createProductCard(product);
        scrollDiv.appendChild(card);
    });
    
    galleryDiv.appendChild(scrollDiv);
    chatContainer.appendChild(galleryDiv);
    scrollToBottom();
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    card.innerHTML = `
        <img src="${product.image}" alt="${product.name}" class="product-image">
        <div class="product-info">
            <div class="product-name">${product.name}</div>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <div class="product-actions">
                <button class="add-to-cart-btn" onclick="addToCart(${product.id})">Add to Cart</button>
                <button class="wishlist-btn" onclick="addToWishlist(${product.id})">♡</button>
            </div>
        </div>
    `;
    
    return card;
}

function handleCategoryClick(category) {
    const products = productDatabase[category];
    if (products) {
        addMessage(`Show me ${category}`, 'user');
        setTimeout(() => {
            addMessage(`Here are some great ${category} items for you:`, 'assistant');
            displayProducts(products);
        }, 800);
    }
}

// Cart Functions
function addToCart(productId) {
    const product = findProductById(productId);
    if (!product) return;
    
    const existingItem = cart.find(item => item.id === productId);
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    
    saveCart();
    updateCartCount();
    updateCartDisplay();
    
    addMessage(`Added ${product.name} to your cart!`, 'assistant');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartCount();
    updateCartDisplay();
}

function updateCartQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (!item) return;
    
    item.quantity += change;
    if (item.quantity <= 0) {
        removeFromCart(productId);
    } else {
        saveCart();
        updateCartDisplay();
    }
}

function updateCartDisplay() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (cart.length === 0) {
        cartItems.innerHTML = '<p class="empty-message">Your cart is empty</p>';
        cartTotal.textContent = '$0.00';
        return;
    }
    
    let total = 0;
    cartItems.innerHTML = '';
    
    cart.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'cart-item';
        
        const subtotal = item.price * item.quantity;
        total += subtotal;
        
        itemDiv.innerHTML = `
            <img src="${item.image}" alt="${item.name}" class="cart-item-image">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                <div class="cart-item-actions">
                    <button class="qty-btn" onclick="updateCartQuantity(${item.id}, -1)">-</button>
                    <span class="cart-item-qty">${item.quantity}</span>
                    <button class="qty-btn" onclick="updateCartQuantity(${item.id}, 1)">+</button>
                    <button class="remove-btn" onclick="removeFromCart(${item.id})">Remove</button>
                </div>
            </div>
        `;
        
        cartItems.appendChild(itemDiv);
    });
    
    cartTotal.textContent = `$${total.toFixed(2)}`;
}

function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cartCount').textContent = count;
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Wishlist Functions
function addToWishlist(productId) {
    const product = findProductById(productId);
    if (!product) return;
    
    const exists = wishlist.find(item => item.id === productId);
    if (!exists) {
        wishlist.push(product);
        saveWishlist();
        updateWishlistCount();
        addMessage(`Added ${product.name} to your wishlist!`, 'assistant');
    } else {
        addMessage(`${product.name} is already in your wishlist!`, 'assistant');
    }
}

function removeFromWishlist(productId) {
    wishlist = wishlist.filter(item => item.id !== productId);
    saveWishlist();
    updateWishlistCount();
    updateWishlistDisplay();
}

function updateWishlistDisplay() {
    const wishlistItems = document.getElementById('wishlistItems');
    
    if (wishlist.length === 0) {
        wishlistItems.innerHTML = '<p class="empty-message">Your wishlist is empty</p>';
        return;
    }
    
    wishlistItems.innerHTML = '';
    
    wishlist.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'cart-item';
        
        itemDiv.innerHTML = `
            <img src="${item.image}" alt="${item.name}" class="cart-item-image">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                <div class="cart-item-actions">
                    <button class="add-to-cart-btn" onclick="addToCart(${item.id})">Add to Cart</button>
                    <button class="remove-btn" onclick="removeFromWishlist(${item.id})">Remove</button>
                </div>
            </div>
        `;
        
        wishlistItems.appendChild(itemDiv);
    });
}

function updateWishlistCount() {
    document.getElementById('wishlistCount').textContent = wishlist.length;
}

function saveWishlist() {
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
}

// Utility Functions
function findProductById(id) {
    return Object.values(productDatabase).flat().find(p => p.id === id);
}

function clearChat() {
    chatContainer.innerHTML = `
        <div class="message assistant-message">
            <div class="message-content">
                <p>Hello! 👋 I'm your dedicated Shopping Assistant, here to answer any questions you might have and help you find anything you're looking for. Whether you need electronics, fashion items, home goods, or anything else - I'm here to help! What can I assist you with today?</p>
            </div>
        </div>
    `;
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function openPanel(panel) {
    panel.classList.add('open');
    overlay.classList.add('active');
    
    if (panel === cartPanel) {
        updateCartDisplay();
    } else if (panel === wishlistPanel) {
        updateWishlistDisplay();
    }
}

function closePanel(panel) {
    panel.classList.remove('open');
    overlay.classList.remove('active');
}

function closeAllPanels() {
    cartPanel.classList.remove('open');
    wishlistPanel.classList.remove('open');
    overlay.classList.remove('active');
}
