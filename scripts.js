function onClick(e) {
  target = e.target

  while(
    target &&
    !target.hasAttribute('data-id')
  ) {
    target = target.parentNode
  }

  if(target.classList.contains('js-container'))
    url = '/?c=' + target.getAttribute('data-id')
  else if(target.classList.contains('js-parent'))
    url = '/?c=' + target.getAttribute('data-id')
  else if(target.classList.contains('js-media'))
    url = '/?m=' + target.getAttribute('data-id')

  if (url) {
    if (window.location.pathname + window.location.search != url)
      window.location.href = url
  }
}

var items = document.querySelectorAll(
  [
    '.js-container[data-id]',
    '.js-parent[data-id]',
    '.js-media[data-id]'
  ].join(",")
)
for (var i = 0, il = items.length; i < il; i++) {
  items[i].addEventListener('click', onClick, false)
}
