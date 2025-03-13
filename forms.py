from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField, EmailField, FloatField
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

class NuevaVentaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    producto_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    descuento = FloatField('Descuento (%)', default=0.0, validators=[NumberRange(min=0, max=100)])
    metodo_pago = SelectField('Método de Pago', 
                            choices=[('efectivo', 'Efectivo'), 
                                   ('tarjeta', 'Tarjeta'), 
                                   ('transferencia', 'Transferencia')],
                            default='efectivo')
    notas = TextAreaField('Notas')
    submit = SubmitField('Registrar Venta')

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    documento_identidad = StringField('Documento de Identidad', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Agregar Cliente')
