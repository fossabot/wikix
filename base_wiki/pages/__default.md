{%- macro categories() %}
{%- for c in varargs %}
    <tag>{{ c }}</tag>
{% endfor %}
{% endmacro %}

{%- macro img(src, link_to=none, alt=none) %}
{%- if link_to is not none %}<a href="{{ link_to }}">{% endif %}
<img src="{{ src }}">
{%- if link_to is not none %}</a>{% endif %}
{% endmacro %}
