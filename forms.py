from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    precio = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    codigo = StringField('Código', validators=[DataRequired(), Length(max=50)])
    categoria_id = SelectField('Categoría', validators=[DataRequired()]) # Modificado
    subcategoria = SelectField('Subcategoría', validators=[Optional()])
    proveedor = SelectField('Proveedor', validators=[Optional()])
    imagen = FileField('Imagen', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imágenes permitidas')])
    submit = SubmitField('Guardar Producto')
    
    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        # Placeholders for dynamic population of select fields from database
        # These can be populated in the route before rendering the form
        self.categoria_id.choices = [('', 'Seleccione una categoría')] # Modificado
        self.subcategoria.choices = [('', 'Seleccione una subcategoría')]
        self.proveedor.choices = [('', 'Seleccione un proveedor')]