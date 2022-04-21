document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.post-card').forEach(post => {
        const post_id = post.dataset.post_id;

        if (document.querySelector(`#edit-view${post_id}`)) {
            config_edit_view(post_id);
        }

        config_like_button(post_id);
        
    });
});

function config_like_button(post_id) {
    const like_button = document.querySelector(`#like-button-${post_id}`);
    const likes = document.querySelector(`#post-likes${post_id}`);

    like_button.onclick = function(event) {
        toggle_likes();
        save_likes();
        event.preventDefault();
    }

    function toggle_likes() {
        if (like_button.className === 'dislike') {
            const new_button = like_button;
            new_button.className = 'like';
            new_button.innerHTML = '&#9825;';
            likes.innerHTML = parseInt(likes.innerHTML) - 1;
        } else {
            const new_button = like_button;
            new_button.className = 'dislike';
            new_button.innerHTML = '&#9829;';
            likes.innerHTML = parseInt(likes.innerHTML) + 1;
        }
    }

    function save_likes() {
        fetch('/like', {
            method: 'PUT',
            body: JSON.stringify({
                post_id: post_id,
            }),
            credentials: 'same-origin',
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(response => {
            if (!response.ok) {
                window.location.replace("/login")
            }
            return response.json()
        })
        .then(result => {
            console.log(result)
        });
    }
}

function config_edit_view(post_id) {
    const edit_button = document.querySelector(`#edit-button-${post_id}`);
    const edited_post_form = document.querySelector(`#edited-post-form-${post_id}`);
    const content = document.querySelector(`#post${post_id}`);
    const new_post_textarea = document.querySelector(`#new-post-content-${post_id}`);

    edit_button.onclick = function(event) {
        toggle_form_visibility();
        event.preventDefault();
    }

    edited_post_form.onsubmit = function(event) {
        save_edited_post();
        event.preventDefault();
    }

    function toggle_form_visibility() {
        new_post_textarea.value = content.innerHTML;

        if (content.style.display === 'none') {
            content.style.display = 'block';
            edited_post_form.style.display = 'none';
        } else {
            content.style.display = 'none';
            edited_post_form.style.display = 'block';
        }
    }

    function save_edited_post() {
        fetch('/edit', {
            method: 'PUT',
            body: JSON.stringify({
                post_id: post_id,
                content: new_post_textarea.value
            }),
            credentials: 'same-origin',
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.content) {
                content.innerHTML = result.content;
            }
            toggle_form_visibility();
        });
    }
}

// This function is copied from: https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
// It gets the csrf token value from the browser's cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }