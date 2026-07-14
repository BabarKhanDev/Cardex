async function generate_card(
    id,
    image_large,
    image_small,
    wishlist_count = 0,
    library_count = 0,
    show_wishlist = true,
    delete_if_wishlist_zero = false,
    show_library = true,
    can_generate_big_card = true,
) {

    let img_element = document.createElement("img")
    img_element.alt = name + " card"
    img_element.className = "card_image"
    img_element.src = image_small
    
if (can_generate_big_card) {
        img_element.onclick = async () => generate_big_card(image_large, name + " card")
    }

    let card_element = document.createElement("div")
    card_element.className = "card"
    card_element.wishlist_id = id
    card_element.append(img_element)

    if (show_wishlist) {
        let wishlist_container = create_wishlist_container(id, delete_if_wishlist_zero, wishlist_count)
        card_element.append(wishlist_container)
    }

    if (show_library) {
        let library_container = create_library_container(id, library_count)
        card_element.append(library_container)
    }

    return card_element
}

async function generate_uploaded_card(image_path, upload_id) {
    let img_element = document.createElement("img")
    img_element.alt = "Uploaded card"
    img_element.className =  "img_library card_image"
    img_element.src = image_path
    img_element.onclick = async () => generate_match_resolver(image_path, upload_id)

    return img_element
}

async function update_wishlist(id, amount, delete_if_wishlist_zero) {
    let formData = new FormData();
    formData.append('card_id', id);
    formData.append('amount', amount);

    let response = await fetch("/wishlist_id", {
        method: 'POST',
        body: formData
    })

    let wishlist = await response.json()
    let counter = document.getElementById("wishlist_count_" + id);

    // if we un-wishlist then id will not be in the wishlist dictionary
    if (id in wishlist) {
        counter.innerText = "Wishlist: " + String(wishlist[id])
    } else {
        if (delete_if_wishlist_zero) {
            let card_container = document.querySelector('[wishlist_id=' + id + ']');
            card_container.remove()
        } else {
            counter.innerText = "In Wishlist: 0"
        }
    }
}

function generate_big_card(imgsrc, alt) {

    let img_element = document.createElement("img")
    img_element.alt = alt
    img_element.className = "big_card_image"
    img_element.src = imgsrc

    let close_button = document.createElement("span")
    close_button.classList.add("big_card_close", "material-symbols-outlined")
    close_button.innerHTML = 'close'
    close_button.onclick = () => close_menus()

    let big_card_container = document.createElement("div")
    big_card_container.className = "big_card_container"
    big_card_container.append(close_button, img_element)

    document.body.appendChild(big_card_container)

}

async function generate_match_resolver(imgsrc, upload_id) {

    let match_resolver_container = document.createElement("div")
    match_resolver_container.className = "match_resolver_container"

    // First row - our image, takes up 2/3 of the page
    let img_element = document.createElement("img")
    img_element.className = "big_card_image"
    img_element.src = imgsrc

    // Second row - our matches, takes up 1/3 of the page
    // match list can be a row element with each match in it
    let matches_element = document.createElement("div")
    matches_element.className = "matches_element"
    let response = await fetch("/matches/" + upload_id)
    let matches = await response.json()
    for (const match of matches) {
        let response = await fetch("/card/" + match.card_id)
        let card_details = await response.json()
        let potential_match = await generate_card(
            card_details.id,
            card_details.image_url_large,
            card_details.image_url_small,
            0,
            0,
            false,
            false,
            false,
            false
        )
        potential_match.onclick = () => submit_match(upload_id, card_details.id)
        matches_element.appendChild(potential_match);
    }

    let close_button = document.createElement("span")
    close_button.classList.add("big_card_close", "material-symbols-outlined")
    close_button.innerHTML = 'close'
    close_button.onclick = () => close_menus()

    match_resolver_container.append(img_element, matches_element, close_button)
    document.body.appendChild(match_resolver_container)

}

function close_menus() {
    let cards = document.querySelectorAll(".match_resolver_container,.big_card_container")
    cards.forEach(card => {
        card.remove()
    })
}

document.onkeydown = function (evt) {
    evt = evt || window.event;
    if (evt.key === "Escape") {
        close_menus()
    }
};

function create_wishlist_container(id, delete_if_wishlist_zero, wishlist_amount) {
    let wishlist_add = document.createElement("div")
    wishlist_add.className = "wishlist_add"
    wishlist_add.innerText = "+"
    wishlist_add.onclick = async () => update_wishlist(id, "1")

    let wishlist_sub = document.createElement("div")
    wishlist_sub.className = "wishlist_sub"
    wishlist_sub.innerText = "-"
    wishlist_sub.onclick = async () => await update_wishlist(id, "-1", delete_if_wishlist_zero)

    let wishlist_count = document.createElement("div")
    wishlist_count.className = "wishlist_count"
    wishlist_count.id = "wishlist_count_" + id
    wishlist_count.innerText = "Wishlist: " + wishlist_amount

    let wishlist_container = document.createElement("div")
    wishlist_container.id = "wishlist_container-" + id
    wishlist_container.className = "wishlist_container"
    wishlist_container.append(wishlist_sub, wishlist_count, wishlist_add)

    return wishlist_container
}

function create_library_container(id, library_amount) {
    let library_count = document.createElement("div")
    library_count.className = "library_count"
    library_count.id = "library_count_" + id
    library_count.innerText = "Library: " + library_amount

    let library_container = document.createElement("div")
    library_container.id = "wishlist_container-" + id
    library_container.className = "wishlist_container"
    library_container.append(library_count)

    return library_container
}

async function submit_match(upload_id, card_id) {
    let formData = new FormData()
    formData.append('upload_id', upload_id)
    formData.append('card_id', card_id)

    // TODO make this endpoint
    await fetch("/confirm_match", {
        method: 'POST',
        body: formData
    })

    close_menus()
}
